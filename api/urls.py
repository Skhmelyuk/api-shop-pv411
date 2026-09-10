
from django.urls import path
from .views import ProductCreateListAPIView, OrderListAPIView, ProductDetailDeleteUpdateAPIView, UserOrderListAPIView

app_name = "api"

urlpatterns = [
    path('products/', ProductCreateListAPIView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailDeleteUpdateAPIView.as_view(), name='product_detail'),
    path('orders/', OrderListAPIView.as_view(), name='order_list'),
    path('user-orders/', UserOrderListAPIView.as_view(), name='user_order_list')
]

