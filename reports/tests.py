import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Customer, Product, Sale


class ReportsAPITests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Ana Cliente", email="ana@example.com")
        self.product = Product.objects.create(name="Libro Django", price=Decimal("20.00"), stock=10)
        Sale.objects.create(customer=self.customer, product=self.product, quantity=2,
                            total=Decimal("40.00"), status="PAID")
        Sale.objects.create(customer=self.customer, product=self.product, quantity=1,
                            total=Decimal("20.00"), status="CANCELLED")

    def test_orm_report_filters_and_excludes_cancelled(self):
        response = self.client.get("/api/reports/orm-report/", {"status": "PAID", "search": "Django"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_raw_report_maps_extra_joined_fields(self):
        response = self.client.get("/api/reports/raw-report/", {"status": "PAID"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["customer"], "Ana Cliente")

    def test_sql_insert_requires_post_and_creates_sale(self):
        url = "/api/reports/insert-sql/"
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url, data=json.dumps({"customer_id": self.customer.id,
                                                          "product_id": self.product.id, "quantity": 3}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Sale.objects.filter(quantity=3, status="PENDING").exists())

    def test_sql_update_and_delete(self):
        Sale.objects.create(customer=self.customer, product=self.product, quantity=1,
                            total=Decimal("20.00"), status="PENDING")
        update = self.client.post("/api/reports/bulk-update/", data="{}", content_type="application/json")
        self.assertEqual(update.status_code, 200)
        self.assertFalse(Sale.objects.filter(status="PENDING").exists())
        denied = self.client.post("/api/reports/cleanup/", data="{}", content_type="application/json")
        self.assertEqual(denied.status_code, 400)
        deleted = self.client.post("/api/reports/cleanup/", data='{"confirm": true}', content_type="application/json")
        self.assertEqual(deleted.status_code, 200)
        self.assertFalse(Sale.objects.filter(status="CANCELLED").exists())
