import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True, verbose_name="Slug")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Батьківська категорія",
    )
    image = models.ImageField(upload_to="categories/", null=True, blank=True, verbose_name="Зображення")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent} → {self.name}" if self.parent_id else self.name

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ["order", "name"]


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Категорія",
    )
    brand = models.CharField(max_length=100, blank=True, verbose_name="Бренд")
    description = models.TextField(verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    stock = models.PositiveIntegerField(verbose_name="Кількість на складі")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    image = models.ImageField(upload_to="products/", null=True, blank=True, verbose_name="Зображення")
    instruction = models.FileField(upload_to="instructions/", null=True, blank=True, verbose_name="Інструкція")

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"
        ordering = ["name"]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Продукт")
    image = models.ImageField(upload_to="products/gallery/", verbose_name="Зображення")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return f"{self.product.name} — фото {self.order}"

    class Meta:
        verbose_name = "Фото продукту"
        verbose_name_plural = "Фото продукту"
        ordering = ["order", "id"]


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications", verbose_name="Продукт")
    name = models.CharField(max_length=100, verbose_name="Характеристика")
    value = models.CharField(max_length=255, verbose_name="Значення")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return f"{self.name}: {self.value}"

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Технічні характеристики"
        ordering = ["order", "id"]
        unique_together = ["product", "name"]


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Очікує"
        CONFIRMED = "confirmed", "Підтверджено"
        CANCELLED = "cancelled", "Скасовано"

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID замовлення")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Користувач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name="Статус")
    products = models.ManyToManyField(Product, through="OrderItem", related_name="orders", verbose_name="Продукти")

    def __str__(self):
        return f"Order {self.order_id} ({self.user.username})"

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Замовлення")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items", verbose_name="Продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order: {self.order.order_id})"

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елементи замовлення"
        unique_together = ["order", "product"]
