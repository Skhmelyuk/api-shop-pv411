import pytest
from django.urls import reverse
from model_bakery import baker
from api.models import Product


@pytest.mark.django_db
class TestProductAPI:
    """Тестування ендпоінтів списку та створення товарів."""

    url_list = reverse('api:product_list')

    def test_get_products_anonymous_allowed(self, api_client, sample_product):
        """Анонімний користувач має право переглядати список товарів (AllowAny)."""
        response = api_client.get(self.url_list)
        
        assert response.status_code == 200
        # Якщо увімкнена пагінація - дані в 'results', якщо ні - список
        data = response.data.get('results', response.data)
        assert len(data) >= 1
        assert data[0]['name'] == sample_product.name

    def test_create_product_anonymous_forbidden(self, api_client):
        """Спроба створити товар анонімом має повертати 401 Unauthorized."""
        payload = {
            "name": "Новий товар",
            "description": "Опис",
            "price": "100.00",
            "stock": 5
        }
        response = api_client.post(self.url_list, payload)
        assert response.status_code == 401

    def test_create_product_regular_user_forbidden(self, auth_client):
        """Звичайний покупець не має права створювати товар (403 Forbidden)."""
        payload = {
            "name": "Товар від покупця",
            "description": "Спроба",
            "price": "500.00",
            "stock": 1
        }
        response = auth_client.post(self.url_list, payload)
        assert response.status_code == 403

    def test_create_product_admin_success(self, admin_client):
        """Адміністратор успішно створює новий товар (201 Created)."""
        payload = {
            "name": "Геймерська мишка",
            "description": "RGB миша з високим DPI",
            "price": "1450.00",
            "stock": 25
        }
        response = admin_client.post(self.url_list, payload)
        
        assert response.status_code == 201
        assert response.data['name'] == payload['name']
        assert Product.objects.filter(name=payload['name']).exists()

    @pytest.mark.parametrize("invalid_price, error_text", [
        (-50, "Ціна товару повинна бути більшою за нуль."),
        (0, "Ціна товару повинна бути більшою за нуль."),
    ])
    def test_create_product_invalid_price(self, admin_client, invalid_price, error_text):
        """Валідація ціни товару (не може бути <= 0)."""
        payload = {
            "name": "Мишка з дефектом",
            "description": "Тест",
            "price": invalid_price,
            "stock": 10
        }
        response = admin_client.post(self.url_list, payload)
        assert response.status_code == 400
        assert error_text in str(response.data)

    def test_filter_products_by_search(self, api_client):
        """Перевірка роботи SearchFilter по полю name."""
        baker.make('api.Product', name="Apple iPhone 15")
        baker.make('api.Product', name="Samsung Galaxy S24")

        response = api_client.get(f"{self.url_list}?search=iPhone")
        assert response.status_code == 200
        data = response.data.get('results', response.data)
        assert len(data) == 1
        assert "iPhone" in data[0]['name']

    def test_in_stock_filter_backend(self, api_client, sample_product, out_of_stock_product):
        """InStockFilterBackend повинен повертати лише товари зі stock > 0."""
        response = api_client.get(self.url_list)
        assert response.status_code == 200
        data = response.data.get('results', response.data)
        
        # Товар без залишку не повинен бути у списку
        product_names = [p['name'] for p in data]
        assert sample_product.name in product_names
        assert out_of_stock_product.name not in product_names


@pytest.mark.django_db
class TestProductDetailAPI:
    """Тестування перегляду, редагування та видалення одного товару."""

    def test_get_product_detail_success(self, api_client, sample_product):
        """Детальна інформація про товар доступна всім (200 OK)."""
        url = reverse('api:product_detail', kwargs={'pk': sample_product.pk})
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['id'] == sample_product.id
        assert response.data['name'] == sample_product.name

    def test_delete_product_admin_success(self, admin_client, sample_product):
        """Адміністратор може видалити товар (204 No Content)."""
        url = reverse('api:product_detail', kwargs={'pk': sample_product.pk})
        response = admin_client.delete(url)
        
        assert response.status_code == 204
        assert not Product.objects.filter(pk=sample_product.pk).exists()