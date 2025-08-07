# orders/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, MenuItemViewSet, CustomerViewSet, OrderViewSet, OrderItemViewSet


# Cria uma instância do DefaultRouter

router = DefaultRouter()

# O router criará as URLs CRUD para cada um dos ViewSets
router.register(r'restaurants', RestaurantViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)


urlpatterns = [
    path('', include(router.urls)),
]