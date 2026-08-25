from django.urls import path
from . import views

urlpatterns = [
    path("orm-report/", views.sales_report_orm),
    path("product-ranking/", views.product_ranking_orm),
    path("raw-report/", views.sales_report_raw),
    path("summary/", views.sales_summary_cursor),
    path("bulk-update/", views.bulk_update_status),
    path("cleanup/", views.cleanup_cancelled_sales),
    path("insert-sql/", views.insert_sale_sql),
    path("call-procedure/", views.call_stored_procedure),
]
