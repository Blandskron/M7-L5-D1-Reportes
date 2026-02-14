from django.contrib import admin
from .models import Customer, Product, Sale

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "active", "created_at")
    search_fields = ("name", "email")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "active")
    search_fields = ("name",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "product", "quantity", "total", "status", "sale_date")
    list_filter = ("status", "sale_date")
    search_fields = ("customer__name", "product__name")