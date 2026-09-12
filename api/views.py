from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer, UserRegisterSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from .filters import ProductFilter, InStockFilterBackend 
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.reverse import reverse

User = get_user_model()


class UserRegisterAPIView(generics.CreateAPIView):
    """Реєстрація нового користувача через API"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'register'


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Головна точка входу Shop API.
    Повертає клікабельну карту всіх доступних сервісів.
    """
    return Response({
        'status': 'online',
        'documentation': {
            'swagger_ui': reverse('swagger-ui', request=request, format=format),
            'redoc': reverse('redoc', request=request, format=format),
            'schema': reverse('schema', request=request, format=format),
        },
        'auth': {
            'register': reverse('api:user_register', request=request, format=format),
            'token_obtain': reverse('token_obtain_pair', request=request, format=format),
            'token_refresh': reverse('token_refresh', request=request, format=format),
        },
        'resources': {
            'products': reverse('api:product_list', request=request, format=format),
            'orders': reverse('api:order_list', request=request, format=format),
            'user_orders': reverse('api:user_order_list', request=request, format=format),
        },
        'admin': request.build_absolute_uri('/admin/'),
        'silk': request.build_absolute_uri('/silk/'),
    })

def landing_page(request):
    """Головна титульна сторінка API (Developer Portal)."""
    return render(request, 'index.html')


class ProductCreateListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, InStockFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'stock']
    throttle_scope = 'products' 

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()



class ProductDetailDeleteUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    throttle_scope = 'product_detail' 

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()



class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    throttle_scope = 'order_all_list' 


class UserOrderListAPIView(generics.ListAPIView):
    """Список замовлень поточного авторизованого користувача"""
    queryset = Order.objects.prefetch_related('items__product').all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_scope = 'user_order' 

    def get_queryset(self):
        # Фільтруємо замовлення за поточним користувачем із JWT-токена
        return super().get_queryset().filter(user=self.request.user)