from django.db import models
from django.utils import timezone

# Modelo Cliente
class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),  # Índice para búsquedas rápidas
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


# Modelo Producto
class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.name


# Modelo Venta
class Sale(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("CANCELLED", "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    sale_date = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["sale_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Sale #{self.id}"