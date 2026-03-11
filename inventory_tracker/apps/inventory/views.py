from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from apps.businesses.models import Business, Branch
from apps.businesses.permissions import can_create_product
from inventory.services import reduce_stock
import pandas as pd



@api_view(["POST"])
def create_product(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    # Permission check
    if not can_create_product(request.user, business):
        return Response(
            {"error": "You are not allowed to create products"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(business=business)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def list_products(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    products = Product.objects.filter(business=business)

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)





@api_view(["POST"])
def record_sale(request):

    product_id = request.data.get("product_id")
    branch_id = request.data.get("branch_id")
    quantity = request.data.get("quantity")

    if not product_id or not branch_id or not quantity:
        return Response(
            {"error": "product_id, branch_id and quantity are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        return Response({"error": "Branch not found"}, status=404)

    try:
        reduce_stock(product, branch, int(quantity))
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

    return Response({"message": "Sale recorded"})


@api_view(["POST"])
def bulk_upload_products(request, business_id):

    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    if not can_create_product(request.user, business):
        return Response(
            {"error": "You are not allowed to upload products"},
            status=status.HTTP_403_FORBIDDEN
        )

    file = request.FILES.get("file")

    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    try:

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)

        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)

        else:
            return Response({"error": "Invalid file format"}, status=400)

        created_products = []

        for _, row in df.iterrows():

            product = Product.objects.create(
                business=business,
                name=row["name"],
                sku=row["sku"],
                barcode=row.get("barcode"),
                cost_price=row["cost_price"],
                selling_price=row["selling_price"]
            )

            created_products.append(product.name)

        return Response({
            "message": f"{len(created_products)} products uploaded successfully"
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

#Scan Product

@api_view(["POST"])
def scan_product(request):

    barcode = request.data.get("barcode")
    business_id = request.data.get("business_id")

    if not barcode or not business_id:
        return Response(
            {"error": "barcode and business_id are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        product = Product.objects.get(
            barcode=barcode,
            business_id=business_id
        )
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ProductSerializer(product)

    return Response(serializer.data)