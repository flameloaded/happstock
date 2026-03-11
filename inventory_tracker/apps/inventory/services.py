from django.db import transaction
from .models import Stock


@transaction.atomic
def reduce_stock(product, branch, quantity):

    stock = Stock.objects.get(product=product, branch=branch)

    if stock.quantity < quantity:
        raise ValueError("Not enough stock")

    stock.quantity -= quantity
    stock.save()