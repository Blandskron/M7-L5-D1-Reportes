"""API didáctica: ORM, raw SQL y cursores de Django."""
import json
from datetime import datetime
from decimal import Decimal

from django.db import connection, transaction
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Customer, Product, Sale

VALID_STATUSES = {choice[0] for choice in Sale.STATUS_CHOICES}


class DecimalJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def request_json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def filtered_sales(params):
    """ORM: filtros, Q, exclude, defer y select_related."""
    sales = Sale.objects.select_related("customer", "product").defer("customer__created_at")
    status, search = params.get("status"), params.get("search")
    if status:
        if status not in VALID_STATUSES:
            raise ValueError("status debe ser PENDING, PAID o CANCELLED.")
        sales = sales.filter(status=status)
    if search:
        sales = sales.filter(Q(customer__name__icontains=search) | Q(product__name__icontains=search))
    for value, lookup in ((params.get("start_date"), "sale_date__gte"), (params.get("end_date"), "sale_date__lte")):
        if value:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed)
            sales = sales.filter(**{lookup: parsed})
    return sales.exclude(status="CANCELLED").order_by("-sale_date")


@require_GET
def sales_report_orm(request):
    """5.1: recuperación filtrada con ORM."""
    try:
        sales = filtered_sales(request.GET)
    except ValueError as exc:
        return error(str(exc))
    data = list(sales.values("id", "customer__name", "product__name", "quantity", "total", "status", "sale_date"))
    return JsonResponse({"count": len(data), "results": data})


@require_GET
def product_ranking_orm(request):
    """Anotaciones ORM: agrega unidades, ventas e ingresos por producto."""
    ranking = (Sale.objects.exclude(status="CANCELLED").values("product_id", "product__name")
               .annotate(sales_count=Count("id"), units_sold=Sum("quantity"), revenue=Sum("total"))
               .order_by("-revenue"))
    return JsonResponse({"results": list(ranking)}, encoder=DecimalJSONEncoder)


@require_GET
def sales_report_raw(request):
    """5.2: raw() mapea columnas a Sale y aliases a atributos extra."""
    status = request.GET.get("status", "PAID")
    if status not in VALID_STATUSES:
        return error("status debe ser PENDING, PAID o CANCELLED.")
    query = """
        SELECT s.id, s.customer_id, s.product_id, s.quantity, s.total, s.status, s.sale_date,
               c.name AS customer_name, p.name AS product_name
        FROM reports_sale s
        JOIN reports_customer c ON c.id = s.customer_id
        JOIN reports_product p ON p.id = s.product_id
        WHERE s.status = %s ORDER BY s.sale_date DESC
    """
    # raw() necesita la PK; %s mantiene la consulta parametrizada en cualquier motor.
    sales = Sale.objects.raw(query, [status])
    data = [{"id": sale.id, "customer": sale.customer_name, "product": sale.product_name,
             "quantity": sale.quantity, "total": float(sale.total), "status": sale.status,
             "sale_date": sale.sale_date} for sale in sales]
    return JsonResponse({"results": data})


@require_GET
def sales_summary_cursor(request):
    """SQL personalizado de lectura con conexión y cursor."""
    with connection.cursor() as cursor:
        cursor.execute("""SELECT status, COUNT(*) AS sales_count, COALESCE(SUM(total), 0) AS revenue
                          FROM reports_sale GROUP BY status ORDER BY status""")
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return JsonResponse({"results": rows}, encoder=DecimalJSONEncoder)


@require_POST
def insert_sale_sql(request):
    """5.3 CREATE SQL. JSON: customer_id, product_id, quantity."""
    payload = request_json(request)
    if payload is None:
        return error("El cuerpo debe ser JSON válido.")
    try:
        customer_id, product_id, quantity = int(payload["customer_id"]), int(payload["product_id"]), int(payload["quantity"])
        if quantity < 1:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        return error("customer_id, product_id y quantity (entero positivo) son obligatorios.")
    try:
        customer = Customer.objects.get(pk=customer_id, active=True)
        product = Product.objects.get(pk=product_id, active=True)
    except (Customer.DoesNotExist, Product.DoesNotExist):
        return error("Cliente o producto activo no encontrado.", 404)
    if product.stock < quantity:
        return error("Stock insuficiente.")
    with transaction.atomic(), connection.cursor() as cursor:
        sql = """INSERT INTO reports_sale (customer_id, product_id, quantity, total, status, sale_date)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        values = [customer.id, product.id, quantity, product.price * quantity, "PENDING", timezone.now()]
        if connection.vendor == "postgresql":
            cursor.execute(sql + " RETURNING id", values)
            sale_id = cursor.fetchone()[0]
        else:
            cursor.execute(sql, values)
            sale_id = cursor.lastrowid
    return JsonResponse({"message": "Venta creada con SQL.", "sale_id": sale_id}, status=201)


@require_POST
def bulk_update_status(request):
    """5.3 UPDATE SQL. JSON opcional: from_status, to_status."""
    payload = request_json(request)
    if payload is None:
        return error("El cuerpo debe ser JSON válido.")
    source, target = payload.get("from_status", "PENDING"), payload.get("to_status", "PAID")
    if source not in VALID_STATUSES or target not in VALID_STATUSES:
        return error("Estados inválidos.")
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("UPDATE reports_sale SET status = %s WHERE status = %s", [target, source])
        updated = cursor.rowcount
    return JsonResponse({"message": "Ventas actualizadas con SQL.", "updated": updated})


@require_POST
def cleanup_cancelled_sales(request):
    """5.3 DELETE SQL protegido por confirmación explícita."""
    payload = request_json(request)
    if payload is None or payload.get("confirm") is not True:
        return error("Envía {\"confirm\": true} para borrar ventas CANCELLED.")
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("DELETE FROM reports_sale WHERE status = %s", ["CANCELLED"])
        deleted = cursor.rowcount
    return JsonResponse({"message": "Ventas anuladas eliminadas con SQL.", "deleted": deleted})


@require_POST
def call_stored_procedure(request):
    """Invoca el procedimiento PostgreSQL creado en la migración 0002."""
    if connection.vendor != "postgresql":
        return error("La demostración requiere PostgreSQL (Docker).", 409)
    payload = request_json(request)
    if payload is None:
        return error("El cuerpo debe ser JSON válido.")
    try:
        customer_id = int(payload["customer_id"])
    except (KeyError, TypeError, ValueError):
        return error("customer_id es obligatorio.")
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("CALL reports_mark_customer_pending_paid(%s)", [customer_id])
    return JsonResponse({"message": "Procedimiento almacenado ejecutado."})
