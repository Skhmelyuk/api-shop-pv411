from decimal import Decimal
from django.core.management.base import BaseCommand
from api.models import User, Product, Order, OrderItem


class Command(BaseCommand):
    help = "Заповнює базу даних тестовими даними"

    def handle(self, *args, **kwargs):
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()

        # Тестовий користувач
        user, _ = User.objects.get_or_create(username="skhmelyuk", email="skhmelyuk@example.com")
        user.set_password("qwerty_1985")
        user.save()

        # Створення продуктів
        products_data = [
            {"name": "Ноутбук Dell XPS 15", "description": "Потужний ноутбук для роботи", "price": Decimal("45000.00"), "stock": 10},
            {"name": "iPhone 15 Pro", "description": "Флагманський смартфон Apple", "price": Decimal("38000.00"), "stock": 15},
            {"name": "Samsung Galaxy S24", "description": "Флагманський смартфон на Android", "price": Decimal("32000.00"), "stock": 20},
            {"name": "AirPods Pro 2", "description": "Бездротові навушники з ANC", "price": Decimal("8500.00"), "stock": 50},
            {"name": "iPad Air M2", "description": "Планшет для творчості", "price": Decimal("24000.00"), "stock": 12},
            {"name": "Sony WH-1000XM5", "description": "Повнорозмірні навушники", "price": Decimal("12500.00"), "stock": 8},
            {"name": "Apple Watch Series 9", "description": "Смарт-годинник для здоров'я", "price": Decimal("14000.00"), "stock": 25},
            {"name": "Монітор LG UltraFine 27\"", "description": "4K IPS монітор", "price": Decimal("16000.00"), "stock": 0},
        ]

        products = [Product.objects.create(**item) for item in products_data]

        # Замовлення 1 (Підтверджено)
        order1 = Order.objects.create(user=user, status=Order.StatusChoices.CONFIRMED)
        OrderItem.objects.create(order=order1, product=products[0], quantity=1)
        OrderItem.objects.create(order=order1, product=products[3], quantity=2)

        # Замовлення 2 (Очікує обробки)
        order2 = Order.objects.create(user=user, status=Order.StatusChoices.PENDING)
        OrderItem.objects.create(order=order2, product=products[1], quantity=1)
        OrderItem.objects.create(order=order2, product=products[4], quantity=1)

        # Замовлення 3 (Скасовано)
        order3 = Order.objects.create(user=user, status=Order.StatusChoices.CANCELLED)
        OrderItem.objects.create(order=order3, product=products[2], quantity=1)
        OrderItem.objects.create(order=order3, product=products[5], quantity=1)

        self.stdout.write(self.style.SUCCESS(
            f"✅ БД заповнено: {Product.objects.count()} продуктів, {Order.objects.count()} замовлень, {OrderItem.objects.count()} позицій."
        ))