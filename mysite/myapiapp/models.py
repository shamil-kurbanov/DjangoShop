from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"Book(title={self.title!r}, author={self.author!r})"