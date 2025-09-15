from django.db import models
from happsaminventory import settings
from core.models import  User

class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=50, unique=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    @property
    def potential_revenue(self):
        return self.selling_price * self.quantity

    @property
    def potential_profit(self):
        return (self.selling_price - self.cost_price) * self.quantity





class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

