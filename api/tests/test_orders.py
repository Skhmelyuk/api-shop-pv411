import pytest
from django.urls import reverse
from model_bakery import baker


@pytest.mark.django_db
class TestOrderPermissions:
    """Тестування прав доступу до замовлень."""

    url_all_orders = reverse('api:order_list')
    url_user_orders = reverse('api:user_order_list')

    def test_all_orders_anonymous_forbidden(self, api_client):
        """Анонім не має доступу до списку всіх замовлень (401)."""
        response = api_client.get(self.url_all_orders)
        assert response.status_code == 401

    def test_all_orders_regular_user_forbidden(self, auth_client):
        """Звичайний покупець не може бачити чужі замовлення у /api/orders/ (403)."""
        response = auth_client.get(self.url_all_orders)
        assert response.status_code == 403

    def test_all_orders_admin_allowed(self, admin_client):
        """Адміністратор має повний доступ до /api/orders/ (200 OK)."""
        baker.make('api.Order', _quantity=3)
        response = admin_client.get(self.url_all_orders)
        
        assert response.status_code == 200
        data = response.data.get('results', response.data)
        assert len(data) == 3

    def test_user_orders_only_returns_own_orders(self, api_client, sample_user):
        """/api/user-orders/ повертає виключно замовлення авторизованого користувача."""
        other_user = baker.make('api.User', username="other_user")
        
        # Створюємо 2 замовлення для нашого користувача і 1 для чужого
        baker.make('api.Order', user=sample_user, _quantity=2)
        baker.make('api.Order', user=other_user, _quantity=1)

        api_client.force_authenticate(user=sample_user)
        response = api_client.get(self.url_user_orders)

        assert response.status_code == 200
        data = response.data.get('results', response.data)
        assert len(data) == 2
        for order in data:
            assert order['user'] == sample_user.id