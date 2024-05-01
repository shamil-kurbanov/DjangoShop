from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product
from typing_extensions import Sequence


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="kurbanov")
        # products: Sequence[Product] = Product.objects.all()
        products: Sequence[Product] = Product.objects.only('id').all()
        order, created = Order.objects.get_or_create(
            delivery_address="Hanover, Prager Str, 78",
            promocode="promo5",
            user=user,
        )
        for product in products:
            order.products.add(product)
        self.stdout.write(f"Created order {order}")
