from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


def product_preview_image(instance, filename):
    """
    Generates the file path for the preview image of a product.

    :param instance: The instance of the product.
    :param filename: The filename of the image.
    :return: The file path of the preview image.
    """
    return 'products/product_{pk}/preview/{filename}'.format(pk=instance.pk, filename=filename)


class Product(models.Model):
    """
    The `Product` class is a model representing a product in the system.

    Attributes:
        name (CharField): The name of the product (max length: 100 characters).
        description (TextField): The description of the product.
        price (DecimalField): The price of the product.
        discount (SmallIntegerField): The discount percentage for the product.
        created_at (DateTimeField): The date and time when the product was created (auto-generated).
        archived (BooleanField): The status of the product (archived or not).
        created_by (ForeignKey): The user who created the product.
        preview (ImageField): An optional preview image for the product.

    Meta:
        ordering (list): A list specifying the default ordering of products (by name and price).
        verbose_name (str): A verbose name for the model.
        verbose_name_plural (str): A verbose plural name for the model.

    Methods:
        __str__(self) -> str:
            Returns a string representation of the product object.

    """

    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    preview = models.ImageField(upload_to=product_preview_image, null=True, blank=True)

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"


class Order(models.Model):
    """
    Represents an order placed by a user.

    :param delivery_address: The delivery address for the order. (optional)
    :type delivery_address: str or None

    :param promocode: The promotional code applied to the order. (optional)
    :type promocode: str or None

    :param created_at: The date and time when the order was created.
    :type created_at: datetime.datetime

    :param user: The user who placed the order.
    :type user: User

    :param products: The products included in the order.
    :type products: QuerySet

    :param receipt: The receipt file associated with the order. (optional)
    :type receipt: File or None
    """
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to="orders/receipts")


@receiver(post_migrate)
def create_custom_permissions(sender, **kwargs):
    """
    Create custom permissions.

    :param sender: The sender object.
    :param kwargs: Additional keyword arguments.
    :return: None
    """
    content_type = ContentType.objects.get_for_model(Product)
    permission, _ = Permission.objects.get_or_create(
        codename='can_create_product',
        name='Can create product',
        content_type=content_type,
    )

