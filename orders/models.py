from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import related 

# Modelo para o Restaurante
class Restaurant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
        ordering = ['name']

    def __str__(self):
        return self.name


# Modelo para Itens do Menu do Restaurante
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Item de Menu"
        verbose_name_plural = "Itens de Menu"
        unique_together = ('restaurant', 'name') # Um item de menu deve ser único por restaurante
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

# Model para o Cliente
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255) # Endereço principal do cliente

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self):
        return self.user.get_full_name() if self.user.get_full_name() else self.user.username


# Model para o Pedido

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PREPARING', 'Em preparo'),
        ('READY_FOR_PICKUP', 'Pronto para Retirada'),
        ('OUT_FOR_DELIVERY', 'Saiu para Entrega'),
        ('DELIVERED', 'Entregue'),
        ('CANCELED', 'Cancelado')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')


    # O entregador é opcional no início do pedido
    delivery_person = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        related_name='assigned_orders',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_address = models.CharField(max_length=255) # Endereço de entrega para este pedido
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer.user.username} ({self.status})"


# Model para os Itens dentro de um Pedido
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Preço do item no momento do pedido

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        unique_together = ('order', 'menu_item') # Um item de menu só pode aparecer uma vez por pedido

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} (Pedido #{self.order.id})"