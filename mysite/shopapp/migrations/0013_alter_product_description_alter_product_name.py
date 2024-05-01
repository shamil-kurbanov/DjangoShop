# Generated by Django 5.0.4 on 2024-04-15 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0012_delete_book'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
