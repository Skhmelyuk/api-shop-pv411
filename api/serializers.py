from rest_framework import serializers
from .models import Product, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Ціна товару повинна бути більшою за нуль.")
        return value

    def validate_stock(self, value):
        if value <= 0:
            raise serializers.ValidationError("Кількість товару повинна бути більшою за нуль.")
        return value

    def validate_name(self, value):
        if len(value) <= 5 and len(value) >= 50:
            raise serializers.ValidationError("Назва товару не може бути порожньою.")
        return value



class OrderItemSerializer(serializers.ModelSerializer):

    # product = ProductSerializer(read_only=True)

    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )


    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_price', 'quantity', 'item_subtotal']


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    def total(self, obj):
        order_items = obj.items.all()
        return sum(item.item_subtotal for item in order_items)


    class Meta:
        model = Order
        fields = ['order_id', 'created_at', 'user', 'status', 'items', 'total_price']