from django.contrib import admin
from .models import User, Product, Order, OrderItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Реєстрація моделі користувача для керування правами та ролями"""
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "in_stock"]
    list_filter = ["stock"]
    search_fields = ["name", "description"]
    readonly_fields = ["in_stock"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ["item_subtotal"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id", "user", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order_id", "user__username"]
    readonly_fields = ["order_id", "created_at"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "item_subtotal"]
    list_filter = ["order__status"]
    readonly_fields = ["item_subtotal"]
