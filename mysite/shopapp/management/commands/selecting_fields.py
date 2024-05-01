from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Product


class Command(BaseCommand):
    # def handle(self, *args, **options):
    #    self.stdout.write("Start demo select fields")
    #    products_values = Product.objects.values('pk', 'name')
    #    with transaction.atomic():
    #        for product in products_values:
    #            self.stdout.write(f"Product ID: {product['pk']}, Name: {product['name']}")
    #    self.stdout.write("Finished demo select fields")

    def handle(self, *args, **options):
        self.stdout.write("Start demo select fields")
        users_info = User.objects.values_list('pk', 'username', 'email')
        with transaction.atomic():
            for user in users_info:
                User.objects.filter(pk=user[0]).update(username=user[1], email=user[2])
                self.stdout.write(f"User ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
                self.stdout.write(self.style.SUCCESS('User {} updated.'.format(user[1])))
                self.stdout.write(self.style.SUCCESS('Done'))

        self.stdout.write("Finished demo select fields")

