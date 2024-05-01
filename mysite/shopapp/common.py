import csv
from io import TextIOWrapper

from .models import Product


def save_csv_products(file, endcoding):
    csv_file = TextIOWrapper(
        file, encoding=endcoding,
    )
    reader = csv.DictReader(csv_file)
    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products
