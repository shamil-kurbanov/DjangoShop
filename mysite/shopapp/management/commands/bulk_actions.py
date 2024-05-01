from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product
from typing_extensions import Sequence


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo bulk actions")

        # List with products properties
        info = [
            ('Smartphone 1', 199),
            ('Smartphone 2', 299),
            ('Smartphone 3', 399),
        ]

        with transaction.atomic():
            # Create products
            # created_by = User.objects.get(username="kurbanov")
            # products = [Product(name=name, price=price, created_by =created_by) for name, price in info]
            # Product.objects.bulk_create(products)
            # self.stdout.write(self.style.SUCCESS('Successfully created products'))

            # Update products
            Product.objects.filter(name__contains='Smartphone').update(discount=15)
            # count all updated products:
            count = Product.objects.filter(name__contains='Smartphone', discount=15).acount()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} products'))

            self.stdout.write(self.style.SUCCESS('Successfully updated products'))

        self.stdout.write("Finished demo bulk actions")
