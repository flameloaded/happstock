from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Product, User, AppSetting
from .serializers import ProductSerializer, UserSerializer,AppSettingSerializer


class AppSettingViewSet(viewsets.ModelViewSet):
    queryset = AppSetting.objects.all()
    serializer_class = AppSettingSerializer
    permission_classes = [permissions.IsAdminUser]  # only admin users can perform any action

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Admins can create/update/delete.
    - Workers can view and update only quantity.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Safe methods: GET, HEAD, OPTIONS (everyone can do these)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Non-safe methods: Check role
        return request.user.role == 'ADMIN' or request.user.role == 'WORKER'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        # Only admin can create new products
        if self.request.user.role != 'ADMIN':
            raise permissions.PermissionDenied("Only admins can add products.")
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # If admin → allow full update
        if request.user.role == 'ADMIN':
            return super().update(request, *args, **kwargs)

        # If worker → allow only quantity update
        if request.user.role == 'WORKER':
            quantity = request.data.get('quantity')
            if quantity is None:
                return Response(
                    {"detail": "Workers can only update the quantity field."},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.quantity = quantity
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        return Response(
            {"detail": "Not authorized."},
            status=status.HTTP_403_FORBIDDEN
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # only admins can create/manage users
