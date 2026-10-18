import django_filters
from django.db.models import Q
from .models import Product
from rest_framework import filters 

class ProductFilter(django_filters.FilterSet):
    category_slug = django_filters.CharFilter(method='filter_category_slug', label='Slug категорії (включно з підкатегоріями)')

    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],
            'price': ['exact', 'lt', 'gt', 'range'],
            'category': ['exact'],
            'brand': ['iexact'],
            'is_new': ['exact'],
        }

    def filter_category_slug(self, queryset, name, value):
        return queryset.filter(Q(category__slug=value) | Q(category__parent__slug=value))

class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0)