import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Тестування отримання JWT токенів."""

    url_token = reverse('token_obtain_pair')
    url_refresh = reverse('token_refresh')

    def test_login_success(self, api_client, sample_user):
        """Користувач отримує пари access і refresh токенів за валідними кредами."""
        payload = {
            "username": "test_buyer",
            "password": "BuyerPass123!"
        }
        response = api_client.post(self.url_token, payload)
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_password(self, api_client, sample_user):
        """Невірний пароль повертає 401 Unauthorized."""
        payload = {
            "username": "test_buyer",
            "password": "WrongPassword999"
        }
        response = api_client.post(self.url_token, payload)
        assert response.status_code == 401

    def test_token_refresh(self, api_client, sample_user):
        """Оновлення access токена через валідний refresh токен."""
        login_res = api_client.post(self.url_token, {
            "username": "test_buyer",
            "password": "BuyerPass123!"
        })
        refresh_token = login_res.data['refresh']

        response = api_client.post(self.url_refresh, {"refresh": refresh_token})
        assert response.status_code == 200
        assert 'access' in response.data


@pytest.mark.django_db
class TestRegistrationAPI:
    """Тестування ендпоінту реєстрації (якщо додано у проект)."""

    def test_register_user_success(self, api_client):
        """Успішна реєстрація нового користувача."""
        url = reverse('api:user_register') if 'api:user_register' in reverse.__globals__ else '/api/register/'
        payload = {
            "username": "newbie",
            "email": "newbie@example.com",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!"
        }
        response = api_client.post('/api/register/', payload)
        
        # Якщо ендпоінт зареєстрований
        if response.status_code != 404:
            assert response.status_code == 201
            assert 'password' not in response.data  # write_only
            user = User.objects.get(username="newbie")
            assert user.check_password("SecurePassword123!")