# Generated by Django 5.0.4 on 2024-04-09 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0011_book_alter_order_options_alter_product_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Book',
        ),
    ]