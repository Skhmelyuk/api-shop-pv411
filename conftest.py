import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker

User = get_user_model()


@pytest.fixture
def api_client():
    """Анонімний тестовий клієнт DRF."""
    return APIClient()


@pytest.fixture
def sample_user(db):
    """Звичайний активний користувач-покупець."""
    return User.objects.create_user(
        username="test_buyer",
        email="buyer@example.com",
        password="BuyerPass123!"
    )


@pytest.fixture
def admin_user(db):
    """Користувач-адміністратор сайту."""
    return User.objects.create_superuser(
        username="admin_user",
        email="admin@example.com",
        password="AdminPass123!"
    )


@pytest.fixture
def auth_client(api_client, sample_user):
    """API-клієнт, авторизований під звичайним користувачем."""
    api_client.force_authenticate(user=sample_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API-клієнт, авторизований під адміністратором."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def sample_product(db):
    """Базовий тестовий товар у наявності."""
    return baker.make(
        'api.Product',
        name="Ноутбук Asus ROG",
        description="Потужний ігровий ноутбук",
        price=35000.00,
        stock=10
    )


@pytest.fixture
def out_of_stock_product(db):
    """Товар, якого немає на складі."""
    return baker.make(
        'api.Product',
        name="Старий телефон",
        price=1200.00,
        stock=0
    )