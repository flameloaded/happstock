from django.db import models
from django.db.models import Q
from apps.businesses.models import Business, Branch
from apps.core.models import User


# =========================
# PRODUCT
# =========================

class Product(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=255)

    sku = models.CharField(max_length=100)

    barcode = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )

    unit = models.CharField(
        max_length=20,
        default="pcs",
        help_text="Unit of measurement e.g pcs, kg, litre"
    )

    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        help_text="Alert when stock falls below this level"
    )

    track_expiry = models.BooleanField(
        default=False,
        help_text="Enable batch expiry tracking for this product"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        constraints = [

            # SKU must be unique per business
            models.UniqueConstraint(
                fields=["business", "sku"],
                name="unique_business_sku"
            ),

            # Barcode must be unique per business (if provided)
            models.UniqueConstraint(
                fields=["business", "barcode"],
                name="unique_business_barcode",
                condition=Q(barcode__isnull=False)
            ),
        ]

        indexes = [
            models.Index(fields=["business"]),
            models.Index(fields=["barcode"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"


# =========================
# PRODUCT BATCH
# =========================

class ProductBatch(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="batches"
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="product_batches"
    )

    batch_number = models.CharField(max_length=100)

    quantity = models.PositiveIntegerField(default=0)

    expiry_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        constraints = [

            # Prevent duplicate batch for same product + branch
            models.UniqueConstraint(
                fields=["product", "branch", "batch_number"],
                name="unique_product_batch"
            ),

            # Prevent negative quantity
            models.CheckConstraint(
                check=Q(quantity__gte=0),
                name="batch_quantity_not_negative"
            ),
        ]

        indexes = [
            models.Index(fields=["product", "branch"]),
            models.Index(fields=["expiry_date"]),
            models.Index(fields=["branch", "expiry_date"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.batch_number}"


# =========================
# STOCK SUMMARY
# =========================

class Stock(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_records"
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="stock_records"
    )

    quantity = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        constraints = [

            # Only one stock record per product per branch
            models.UniqueConstraint(
                fields=["product", "branch"],
                name="unique_product_branch_stock"
            ),

            # Prevent negative stock
            models.CheckConstraint(
                check=Q(quantity__gte=0),
                name="stock_quantity_not_negative"
            ),
        ]

        indexes = [
            models.Index(fields=["product", "branch"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.branch.name}"


# =========================
# STOCK MOVEMENT (LEDGER)
# =========================

class StockMovement(models.Model):

    MOVEMENT_TYPES = (
        ("purchase", "Purchase"),
        ("sale", "Sale"),
        ("adjustment", "Adjustment"),
        ("transfer_in", "Transfer In"),
        ("transfer_out", "Transfer Out"),
        ("damage", "Damage"),
        ("expired", "Expired"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="movements"
    )

    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES
    )

    quantity = models.IntegerField()

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["movement_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.product.name} {self.movement_type} {self.quantity}"