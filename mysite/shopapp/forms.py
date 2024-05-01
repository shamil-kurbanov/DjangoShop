from django.contrib.auth.models import Group
from django.forms import ModelForm, forms

from shopapp.models import Product, Order


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'discount']


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'promocode', 'user', 'products']


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name']


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')