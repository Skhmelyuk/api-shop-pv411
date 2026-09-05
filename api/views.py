from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from rest_framework.response import Response


@api_view(["GET"])
def product_list(request):
    products = Product.objects.all()
    serialiser = ProductSerializer(products, many=True)
    return Response(serialiser.data)


@api_view(['GET'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
def order_list(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)