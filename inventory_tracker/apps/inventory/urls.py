from django.urls import path

from .views import (
    create_product,
    list_products,
    record_sale,
    bulk_upload_products,
    scan_product,
)

urlpatterns = [

    # -----------------------------
    # PRODUCTS
    # -----------------------------

    # Create a product
    path(
        "products/create/<int:business_id>/",
        create_product,
        name="create_product"
    ),

    path("products/scan/", scan_product, name="scan_product"),
    # List all products in a business
    path(
        "products/<int:business_id>/",
        list_products,
        name="list_products"
    ),

    # Bulk upload products
    path(
        "products/bulk-upload/<int:business_id>/",
        bulk_upload_products,
        name="bulk_upload_products"
    ),

    # -----------------------------
    # SALES
    # -----------------------------

    # Record a sale
    path(
        "sales/record/",
        record_sale,
        name="record_sale"
    ),

]