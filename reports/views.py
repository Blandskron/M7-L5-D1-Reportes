from django.db import connection
from django.db.models import Sum, F, Q, Count
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from .models import Sale, Customer, Product


# ===============================
# 5.1 CONSULTAS ORM CON FILTROS
# ===============================
def sales_report_orm(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    status = request.GET.get("status")
    search = request.GET.get("search")

    sales = Sale.objects.select_related("customer", "product")

    # Filtro por rango de fechas
    if start_date and end_date:
        sales = sales.filter(sale_date__range=[parse_datetime(start_date), parse_datetime(end_date)])

    # Filtro por estado
    if status:
        sales = sales.filter(status=status)

    # Búsqueda parcial en nombre cliente o producto
    if search:
        sales = sales.filter(
            Q(customer__name__icontains=search) |
            Q(product__name__icontains=search)
        )

    # Exclusión de canceladas
    sales = sales.exclude(status="CANCELLED")

    # Anotaciones (agregaciones)
    sales = sales.annotate(total_quantity=Sum("quantity"))

    # Ordenamiento
    sales = sales.order_by("-sale_date")

    data = list(sales.values(
        "id",
        "customer__name",
        "product__name",
        "quantity",
        "total",
        "status",
        "sale_date",
        "total_quantity"
    ))

    return JsonResponse(data, safe=False)


# ==========================================
# 5.2 SQL RAW CON FILTROS Y MAPEOS
# ==========================================
def sales_report_raw(request):
    status = request.GET.get("status", "PAID")

    query = """
        SELECT s.id, s.customer_id, s.product_id,
               s.quantity, s.total, s.status, s.sale_date
        FROM reports_sale s
        WHERE s.status = %s
        ORDER BY s.sale_date DESC
    """

    sales = Sale.objects.raw(query, [status])  # Paso de parámetros

    data = []
    for sale in sales:
        data.append({
            "id": sale.id,
            "customer_id": sale.customer_id,
            "product_id": sale.product_id,
            "quantity": sale.quantity,
            "total": float(sale.total),
            "status": sale.status,
            "sale_date": sale.sale_date,
        })

    return JsonResponse(data, safe=False)


# ==========================================
# SQL PERSONALIZADO CON CURSOR
# ==========================================
def sales_summary_cursor(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT status, COUNT(*), SUM(total)
            FROM reports_sale
            GROUP BY status
        """)
        rows = cursor.fetchall()

    data = [
        {"status": row[0], "count": row[1], "total": float(row[2] or 0)}
        for row in rows
    ]

    return JsonResponse(data, safe=False)


# ==========================================
# 5.3 CRUD CON SQL DIRECTO
# ==========================================

# UPDATE masivo por SQL
def bulk_update_status(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE reports_sale
            SET status = 'PAID'
            WHERE status = 'PENDING'
        """)

    return JsonResponse({"message": "Bulk update executed"})


# DELETE controlado por SQL
def cleanup_cancelled_sales(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM reports_sale
            WHERE status = 'CANCELLED'
        """)

    return JsonResponse({"message": "Cancelled sales deleted"})


# INSERT directo por SQL
def insert_sale_sql(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO reports_sale (customer_id, product_id, quantity, total, status, sale_date)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, [1, 1, 2, 2000, "PAID"])

    return JsonResponse({"message": "Sale inserted via SQL"})


# CALL PROCEDURE (si existe en BD)
def call_stored_procedure(request):
    with connection.cursor() as cursor:
        cursor.callproc("my_sales_procedure", [1])  # Parámetro ejemplo

    return JsonResponse({"message": "Stored procedure executed"})