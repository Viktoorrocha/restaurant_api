# orders.views.py 

from rest_framework import viewsets
from .models import Restaurant, MenuItem, Customer, Order, OrderItem
from .serializers import RestaurantSerializer, MenuItemSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer

# ViewsSet para o modelo Restaurant
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer 


# ViewSet para o modelo MenuItem
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


# ViewSet para o modelo Customer
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# ViewSet para o modelo OrderItem
# Geralmente, OrderItem é gerenciado via Order, mas podemos ter um ViewSet para ele se precisarmos de acesso direto
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

# ViewSet para o modelo Order (Pedido)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer