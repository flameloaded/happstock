from rest_framework import serializers
from .models import Product, ProductBatch


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["business", "created_at"]


class ProductBatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductBatch
        fields = "__all__"