from random import choices
from string import ascii_letters

from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User, Permission
from django.http import request, JsonResponse
from django.test import TestCase
from django.urls import reverse
from django.views import View
from shopapp.utils import add_two_numbers

from shopapp.models import Product, Order

from mysite import settings


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(6, 3)
        self.assertEqual(result, 9)


class ProductCreateViewTestCase(TestCase):

    def setUp(self):
        # Generate a random product name
        self.product_name = ''.join(choices(ascii_letters, k=10))

    def test_create_product(self):
        # Send a POST request to create a product
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': self.product_name,
                'price': '123.45',
                'description': 'A good table',
                'discount': '10',
            }
        )
        print(response.url)
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='bob_test', password='qwerty')
        cls.user.is_staff = True
        cls.user.save()
        # Add permission to view orders
        view_order_permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(view_order_permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        # self.assertContains(response, ' You do not have permission to view this page')
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)
        # self.assertRedirects(response, str(settings.LOGIN_URL))


class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        orders = Order.objects.select_related('user').prefetch_related('products').all()
        data = []
        for order in orders:
            order_data = {
                'order_id': order.pk,
                'address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user_id,
                'product_ids': list(order.products.values_list('pk', flat=True))
            }
            data.append(order_data)
        return JsonResponse(data, safe=False)


class OrdersExportViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user with staff status
        cls.user = User.objects.create_user(username='test_user', password='password', is_staff=True)
        # Add permission to view orders
        view_order_permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(view_order_permission)

    def test_create_product(self):
        # Send a POST request to create a product
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': self.product_name,
                'price': '123.45',
                'description': 'A good table',
                'discount': '10',
            }
        )
        print(response.url)
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())

    def setUp(self):
        self.client.force_login(self.user)
        # Create some orders for testing
        self.order = Order.objects.create(user=self.user, promocode='TEST123', delivery_address='123 Test Street 1')
        # Create some products
        # Add products to orders
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': 'table',
                'price': '123.45',
                'description': 'A good table',
                'discount': '10',
            }
        )
        self.assertTrue(Product.objects.filter(name='table').exists())
        self.order.products.add(response)

    def tearDown(self):
        # Clean up
        self.order.delete()
        self.product.delete()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def test_orders_export_view(self):
        response = self.client.get(reverse('shopapp:orders_export'))
        self.assertEqual(response.status_code, 200)
        expected_data = [
            {
                'order_id': self.order.pk,
                'address': self.order.delivery_address,
                'promocode': self.order.promocode,
                'user_id': self.user.pk,
                'product_ids': [self.product.pk]
            }
        ]
        self.assertListEqual(response.json(), expected_data)


# New view and its test
class TestView(TestCase):
    def test_example(self):
        response = self.client.get(reverse('shopapp:example_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is an example view.")
