from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Product, AppSetting

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User  # your custom user model



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'quantity', 'cost_price', 'selling_price', 'created_at')
    search_fields = ('name', 'barcode')
    list_filter = ('category', 'created_at')
    readonly_fields = ('created_at',)

    # Restrict adding products to only ADMIN role
    def has_add_permission(self, request):
        return request.user.role == 'ADMIN'

    # Restrict editing products to only ADMIN role
    def has_change_permission(self, request, obj=None):
        return request.user.role == 'ADMIN'

    # Restrict deleting products to only ADMIN role
    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'ADMIN'


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_by', 'updated_at')
    search_fields = ('key',)
    readonly_fields = ('updated_at',)
