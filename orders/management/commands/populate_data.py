# orders/management/commands/populate_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from orders.models import Restaurant, MenuItem, Customer, Order, OrderItem
from faker import Faker
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo para o projeto de pedidos de restaurante.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando a população do banco de dados para a API de Pedidos de Restaurante...'))

        fake = Faker('pt_BR')

        # Limpar dados existentes (opcional, mas bom para testes repetitivos)
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        MenuItem.objects.all().delete()
        Restaurant.objects.all().delete()
        Customer.objects.all().delete()
        # Cuidado ao deletar Users, pois pode apagar seu superusuário!
        # Vamos apenas garantir que não haja Customer sem User.
        self.stdout.write(self.style.WARNING('Dados de Pedidos, Itens de Menu, Restaurantes e Clientes limpos.'))

        # --- 1. Criar Restaurantes ---
        self.stdout.write(self.style.HTTP_INFO('Criando restaurantes...'))
        restaurantes_criados = []
        nomes_restaurantes = [
            "Sabor Brasileiro", "Pizzaria Imperial", "Sushi Express",
            "Hamburgueria Gourmet", "Cantina Italiana", "Tempero Indiano",
            "Café da Esquina", "Mexicano Fiesta", "Salad & Co.", "Churrascaria Gaúcha"
        ]
        for nome_rest in nomes_restaurantes:
            restaurante, created = Restaurant.objects.get_or_create(
                name=nome_rest,
                defaults={
                    'address': fake.address(),
                    'phone_number': fake.phone_number(),
                    'is_active': True
                }
            )
            restaurantes_criados.append(restaurante)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Restaurante "{nome_rest}" criado.'))

        if not restaurantes_criados:
            self.stdout.write(self.style.ERROR('Nenhum restaurante foi criado. Abortando populacão de itens de menu e pedidos.'))
            return

        # --- 2. Criar Itens de Menu para cada Restaurante ---
        self.stdout.write(self.style.HTTP_INFO('Criando itens de menu...'))
        itens_menu_criados = []
        for restaurante in restaurantes_criados:
            num_itens = random.randint(5, 10)
            for _ in range(num_itens):
                item_name = fake.unique.word().capitalize() + ' ' + random.choice(['Burguer', 'Pizza', 'Salada', 'Frango', 'Massa', 'Sobremesa', 'Bebida'])
                menu_item, created = MenuItem.objects.get_or_create(
                    restaurant=restaurante,
                    name=item_name,
                    defaults={
                        'description': fake.text(max_nb_chars=100),
                        'price': round(random.uniform(15.00, 80.00), 2),
                        'is_available': True
                    }
                )
                itens_menu_criados.append(menu_item)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Item "{item_name}" para {restaurante.name} criado.'))
            # Resetar o gerador 'unique' do Faker para evitar falhas em grandes volumes de dados
            fake = Faker('pt_BR')


        if not itens_menu_criados:
            self.stdout.write(self.style.ERROR('Nenhum item de menu foi criado. Abortando populacão de clientes e pedidos.'))
            return

        # --- 3. Criar Clientes ---
        self.stdout.write(self.style.HTTP_INFO('Criando clientes...'))
        clientes_criados = []
        num_clientes = 5
        for i in range(num_clientes):
            user_username = f"cliente_{i+1}"
            # Get or create user for the customer
            user, user_created = User.objects.get_or_create(
                username=user_username,
                defaults={
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'email': fake.email(),
                    'password': 'pbkdf2_sha256$260000$Qf8G6pY5Y6tG$R8pY7Y5Y6tG$', # Senha "password" hashed
                }
            )
            if user_created:
                self.stdout.write(self.style.SUCCESS(f'Usuário "{user_username}" criado.'))

            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': fake.phone_number(),
                    'address': fake.address()
                }
            )
            clientes_criados.append(customer)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Cliente "{customer.user.username}" criado.'))

        if not clientes_criados:
            self.stdout.write(self.style.ERROR('Nenhum cliente foi criado. Abortando populacão de pedidos.'))
            return


        # --- 4. Criar Pedidos (incluindo OrderItems) ---
        self.stdout.write(self.style.HTTP_INFO('Criando pedidos...'))
        num_pedidos = 30 # Vamos criar pelo menos 30 pedidos

        # Para simular entregadores, vamos usar alguns dos Users que não são clientes.
        # Por simplicidade, vamos usar o superusuário criado como entregador principal,
        # ou criar um User genérico para isso.
        try:
            delivery_user = User.objects.get(username='admin') # Ou outro username que você criou
        except User.DoesNotExist:
            delivery_user = None
            self.stdout.write(self.style.WARNING('Usuário "admin" não encontrado para atribuição de entregador.'))

        for i in range(num_pedidos):
            random_customer = random.choice(clientes_criados)
            random_restaurant = random.choice(restaurantes_criados)

            # Selecionar itens de menu APENAS do restaurante escolhido
            available_menu_items = MenuItem.objects.filter(restaurant=random_restaurant, is_available=True)
            if not available_menu_items.exists():
                self.stdout.write(self.style.WARNING(f'Restaurante "{random_restaurant.name}" não tem itens de menu. Pulando pedido.'))
                continue

            order_status = random.choice([status[0] for status in Order.STATUS_CHOICES])
            delivery_address = random_customer.address # O endereço de entrega pode ser o do cliente

            pedido = Order.objects.create(
                customer=random_customer,
                restaurant=random_restaurant,
                delivery_person=delivery_user, # Atribui o entregador
                status=order_status,
                delivery_address=delivery_address,
                delivery_notes=fake.sentence(nb_words=6) if random.random() > 0.5 else None # Notas opcionais
            )
            self.stdout.write(self.style.SUCCESS(f'  Pedido #{pedido.id} para {random_customer.user.username} no {random_restaurant.name} ({pedido.status}).'))

            # Adicionar itens ao pedido
            num_order_items = random.randint(1, 5)
            order_total_price = Decimal('0.00')
            items_for_order = random.sample(list(available_menu_items), min(num_order_items, available_menu_items.count()))

            for menu_item in items_for_order:
                quantity = random.randint(1, 3)
                item_price = menu_item.price * quantity
                OrderItem.objects.create(
                    order=pedido,
                    menu_item=menu_item,
                    quantity=quantity,
                    price=menu_item.price # Guarda o preço base do item no momento do pedido
                )
                order_total_price += item_price
                self.stdout.write(self.style.SUCCESS(f'    Adicionado {quantity}x "{menu_item.name}" ao pedido #{pedido.id}.'))

            # Atualizar o preço total do pedido
            pedido.total_price = round(order_total_price, 2)
            pedido.save()

        self.stdout.write(self.style.SUCCESS('População do banco de dados concluída com sucesso!'))