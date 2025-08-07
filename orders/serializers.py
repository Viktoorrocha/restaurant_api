# orders/serializers.py 

from rest_framework import serializers
from .models import Restaurant, MenuItem, Customer, Order, OrderItem
from django.contrib.auth.models import User 
from decimal import Decimal


# Serializers para o modelo User (simplificando para o Customer)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['username']


# Serializers para o modelo Restaurant
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'



# Serializers para o modelo MenuItem
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'



# Serializers para o modelo Customer
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'


# Serializers para os itens dentro de um pedido (OrderItem)
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'price', 'menu_item_name']
        # O campo 'order' não deve ser exigido ao criar um item aninhado
        read_only_fields = ['order', 'price', 'menu_item_name']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True) 
    # Altera o campo 'customer' para aceitar um ID na criação do pedido
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    delivery_person_name = serializers.CharField(source='delivery_person.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'restaurant', 'restaurant_name', 'delivery_person', 
            'delivery_person_name', 'status', 'total_price', 'delivery_address', 
            'delivery_notes', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['total_price', 'created_at', 'updated_at'] 


    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        total_price = Decimal('0.00')

        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']

            # Validação: Garante que o item de menu pertence ao restaurante do pedido
            if menu_item.restaurant != order.restaurant:
                # Limpa o pedido recém-criado para evitar pedidos órfãos
                order.delete()
                raise serializers.ValidationError({
                    'items': f"O item de menu '{menu_item.name}' não pertence ao restaurante '{order.restaurant.name}'."
                })

            # Cria o item do pedido, guardando o preço do momento da compra
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=menu_item.price
            )
            total_price += (menu_item.price * quantity)
        
        # Atualiza o preço total do pedido e salva
        order.total_price = total_price
        order.save()
        
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Atualiza os campos do Pedido (exceto 'items')
        instance = super().update(instance, validated_data)

        if items_data is not None:
            # Abordagem simples para atualização: deleta os itens antigos e cria os novos.
            instance.items.all().delete()
            total_price = Decimal('0.00')

            for item_data in items_data:
                menu_item = item_data['menu_item']
                quantity = item_data['quantity']

                if menu_item.restaurant != instance.restaurant:
                    raise serializers.ValidationError({
                        'items': f"O item de menu '{menu_item.name}' não pertence ao restaurante '{instance.restaurant.name}'."
                    })
                
                OrderItem.objects.create(
                    order=instance,
                    menu_item=menu_item,
                    quantity=quantity,
                    price=menu_item.price
                )
                total_price += (menu_item.price * quantity)
            
            instance.total_price = total_price
            instance.save()
            
        return instance