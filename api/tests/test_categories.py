import pytest
from django.urls import reverse
from model_bakery import baker
from api.models import Category, Product


@pytest.fixture
def catalog(db):
    major = baker.make('api.Category', name="Велика побутова техніка", slug="major-appliances", order=0)
    fridges = baker.make('api.Category', name="Холодильники", slug="refrigerators", parent=major, order=1)
    hobs = baker.make('api.Category', name="Варочні панелі", slug="hobs", parent=major, order=0)
    scooters = baker.make('api.Category', name="Електроскутери", slug="electric-scooters", order=1)
    return {"major": major, "fridges": fridges, "hobs": hobs, "scooters": scooters}


@pytest.mark.django_db
class TestCategoryModel:

    def test_slug_generated_from_name(self):
        category = Category.objects.create(name="Чайники")
        assert category.slug == "чайники"

    def test_str_includes_parent(self, catalog):
        assert str(catalog["fridges"]) == "Велика побутова техніка → Холодильники"
        assert str(catalog["scooters"]) == "Електроскутери"


@pytest.mark.django_db
class TestCategoryAPI:

    def test_tree_returns_groups_with_ordered_children(self, api_client, catalog):
        response = api_client.get(reverse('api:category_list'))

        assert response.status_code == 200
        assert [c['slug'] for c in response.data] == ["major-appliances", "electric-scooters"]
        assert [c['slug'] for c in response.data[0]['children']] == ["hobs", "refrigerators"]
        assert response.data[1]['children'] == []

    def test_detail_by_slug(self, api_client, catalog):
        response = api_client.get(reverse('api:category_detail', kwargs={'slug': 'refrigerators'}))

        assert response.status_code == 200
        assert response.data['name'] == "Холодильники"
        assert response.data['parent'] == catalog["major"].pk


@pytest.mark.django_db
class TestProductCatalogAPI:

    url_list = reverse('api:product_list')

    def test_filter_by_group_slug_includes_subcategories(self, api_client, catalog):
        baker.make('api.Product', name="Холодильник", category=catalog["fridges"], stock=1)
        baker.make('api.Product', name="Варочна панель", category=catalog["hobs"], stock=1)
        baker.make('api.Product', name="Скутер", category=catalog["scooters"], stock=1)

        response = api_client.get(self.url_list, {'category_slug': 'major-appliances'})
        names = {p['name'] for p in response.data['results']}
        assert names == {"Холодильник", "Варочна панель"}

        response = api_client.get(self.url_list, {'category_slug': 'refrigerators'})
        assert [p['name'] for p in response.data['results']] == ["Холодильник"]

    def test_detail_contains_category_and_specifications(self, api_client, catalog):
        product = baker.make('api.Product', category=catalog["scooters"], brand="Liberty", is_new=True)
        baker.make('api.ProductSpecification', product=product, name="Колір", value="Синій", order=1)
        baker.make('api.ProductSpecification', product=product, name="Кількість місць", value="2", order=0)

        response = api_client.get(reverse('api:product_detail', kwargs={'pk': product.pk}))

        assert response.status_code == 200
        assert response.data['category'] == catalog["scooters"].pk
        assert response.data['category_name'] == "Електроскутери"
        assert response.data['is_new'] is True
        assert response.data['specifications'] == [
            {"name": "Кількість місць", "value": "2", "order": 0},
            {"name": "Колір", "value": "Синій", "order": 1},
        ]

    def test_admin_creates_product_with_specifications(self, admin_client, catalog):
        payload = {
            "name": "Liberty Moto Brisk",
            "category": catalog["scooters"].pk,
            "brand": "Liberty",
            "description": "Двомісний електроскутер",
            "price": "52999.00",
            "stock": 5,
            "specifications": [
                {"name": "Максимальна швидкість", "value": "43 км/год", "order": 0},
                {"name": "Потужність двигуна", "value": "2000 W", "order": 1},
            ],
        }
        response = admin_client.post(self.url_list, payload, format='json')

        assert response.status_code == 201
        product = Product.objects.get(name="Liberty Moto Brisk")
        assert product.category == catalog["scooters"]
        assert list(product.specifications.values_list('name', flat=True)) == [
            "Максимальна швидкість", "Потужність двигуна",
        ]

    def test_admin_update_replaces_specifications(self, admin_client, catalog):
        product = baker.make('api.Product', category=catalog["scooters"], price=100, stock=1)
        baker.make('api.ProductSpecification', product=product, name="Колір", value="Синій")

        response = admin_client.patch(
            reverse('api:product_detail', kwargs={'pk': product.pk}),
            {"specifications": [{"name": "Колір", "value": "Чорний"}]},
            format='json',
        )

        assert response.status_code == 200
        assert list(product.specifications.values_list('value', flat=True)) == ["Чорний"]

    def test_duplicate_specification_names_rejected(self, admin_client, catalog):
        payload = {
            "name": "Скутер",
            "description": "Тест",
            "price": "100.00",
            "stock": 1,
            "specifications": [{"name": "Колір", "value": "Синій"}, {"name": "Колір", "value": "Чорний"}],
        }
        response = admin_client.post(self.url_list, payload, format='json')

        assert response.status_code == 400
        assert "Назви характеристик не повинні повторюватися." in str(response.data)
