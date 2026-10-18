from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.db import transaction
from .models import Category, Product, ProductImage, ProductSpecification, Order, OrderItem

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Пароль повинен бути надійним і містити щонайменше 8 символів."
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Повторіть пароль для підтвердження."
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Користувач із цією електронною адресою вже зареєстрований.")
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Паролі не співпадають."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'image', 'order']


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'order', 'children']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ['name', 'value', 'order']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'brand', 'description',
            'price', 'stock', 'is_new', 'image', 'images', 'instruction', 'specifications',
        ]

    def validate_specifications(self, value):
        names = [spec['name'] for spec in value]
        if len(names) != len(set(names)):
            raise serializers.ValidationError("Назви характеристик не повинні повторюватися.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        specifications = validated_data.pop('specifications', [])
        product = super().create(validated_data)
        self._save_specifications(product, specifications)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        specifications = validated_data.pop('specifications', None)
        product = super().update(instance, validated_data)
        if specifications is not None:
            product.specifications.all().delete()
            self._save_specifications(product, specifications)
        return product

    @staticmethod
    def _save_specifications(product, specifications):
        ProductSpecification.objects.bulk_create(
            ProductSpecification(product=product, **spec) for spec in specifications
        )

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