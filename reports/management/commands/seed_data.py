import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from reports.models import Customer, Product, Sale


class Command(BaseCommand):
    help = "Llena la base de datos con datos masivos para pruebas avanzadas ORM y SQL"

    def add_arguments(self, parser):
        parser.add_argument("--customers", type=int, default=200)
        parser.add_argument("--products", type=int, default=100)
        parser.add_argument("--sales", type=int, default=2000)

    def handle(self, *args, **options):
        num_customers = options["customers"]
        num_products = options["products"]
        num_sales = options["sales"]

        self.stdout.write(self.style.WARNING("Eliminando datos anteriores..."))
        Sale.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Creando clientes..."))

        customers = []
        for i in range(num_customers):
            customers.append(Customer(
                name=f"Cliente {i}",
                email=f"cliente{i}@mail.com",
                active=random.choice([True, True, True, False]),
            ))
        Customer.objects.bulk_create(customers)

        customers = list(Customer.objects.all())

        self.stdout.write(self.style.SUCCESS("Creando productos..."))

        products = []
        for i in range(num_products):
            products.append(Product(
                name=f"Producto {i}",
                price=Decimal(random.randint(1000, 100000)),
                stock=random.randint(0, 500),
                active=random.choice([True, True, True, False]),
            ))
        Product.objects.bulk_create(products)

        products = list(Product.objects.all())

        self.stdout.write(self.style.SUCCESS("Creando ventas..."))

        statuses = ["PENDING", "PAID", "CANCELLED"]

        sales_batch = []
        now = timezone.now()

        for i in range(num_sales):
            customer = random.choice(customers)
            product = random.choice(products)
            quantity = random.randint(1, 10)
            total = product.price * quantity

            random_days = random.randint(0, 365)
            random_date = now - timedelta(days=random_days)

            sales_batch.append(Sale(
                customer=customer,
                product=product,
                quantity=quantity,
                total=total,
                status=random.choice(statuses),
                sale_date=random_date
            ))

            # Insertar por lotes para rendimiento
            if len(sales_batch) >= 500:
                Sale.objects.bulk_create(sales_batch)
                sales_batch = []

        if sales_batch:
            Sale.objects.bulk_create(sales_batch)

        self.stdout.write(self.style.SUCCESS("Base de datos poblada correctamente."))