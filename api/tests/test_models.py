import pytest
from decimal import Decimal
from model_bakery import baker
from api.models import Product, Order, OrderItem


@pytest.mark.django_db
class TestProductModel:
    """Тести бізнес-логіки моделі Product."""

    def test_product_str(self, sample_product):
        """Метод __str__ повинен повертати назву товару."""
        assert str(sample_product) == "Ноутбук Asus ROG"

    def test_in_stock_true_when_stock_positive(self, sample_product):
        """Property in_stock має повертати True, якщо stock > 0."""
        assert sample_product.in_stock is True

    def test_in_stock_false_when_stock_zero(self, out_of_stock_product):
        """Property in_stock має повертати False, якщо stock == 0."""
        assert out_of_stock_product.in_stock is False


@pytest.mark.django_db
class TestOrderModel:
    """Тести замовлення та позицій замовлення."""

    def test_order_item_subtotal(self):
        """Перевірка розрахунку item_subtotal (price * quantity)."""
        product = baker.make('api.Product', price=Decimal('250.50'))
        order = baker.make('api.Order')
        item = baker.make('api.OrderItem', order=order, product=product, quantity=3)

        assert item.item_subtotal == Decimal('751.50')

    def test_order_str(self, sample_user):
        """Перевірка стрічкового представлення замовлення."""
        order = baker.make('api.Order', user=sample_user)
        assert sample_user.username in str(order)
        assert str(order.order_id) in str(order)

    def test_order_default_status(self):
        """Нове замовлення за замовчуванням повинно мати статус PENDING."""
        order = baker.make('api.Order')
        assert order.status == Order.StatusChoices.PENDING