from django.contrib import admin
from .models import User, Category, Product, ProductImage, ProductSpecification, Order, OrderItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Реєстрація моделі користувача для керування правами та ролями"""
    pass


class SubcategoryInline(admin.TabularInline):
    model = Category
    fk_name = "parent"
    extra = 0
    fields = ["name", "slug", "image", "order"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "slug", "order"]
    list_filter = ["parent"]
    list_editable = ["order"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [SubcategoryInline]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "brand", "price", "stock", "in_stock", "is_new"]
    list_filter = ["category", "brand", "is_new", "stock"]
    list_select_related = ["category", "category__parent"]
    search_fields = ["name", "description", "brand"]
    readonly_fields = ["in_stock"]
    inlines = [ProductImageInline, ProductSpecificationInline]


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
