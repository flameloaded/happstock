from django.db import models
from apps.inventory.models import Product
from apps.businesses.models import Branch
from apps.core.models import User


class Sale(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    sold_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)