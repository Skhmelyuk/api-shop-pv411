import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    stock = models.PositiveIntegerField(verbose_name="Кількість на складі")
    image = models.ImageField(upload_to="products/", null=True, blank=True, verbose_name="Зображення")

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"
        ordering = ["name"]


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
