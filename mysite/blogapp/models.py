from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(_("Title"), max_length=200)
    content = models.TextField(_("Content"))
    pub_date = models.DateTimeField(_("Publication Date"), null=True, blank=True)
    last_modified = models.DateTimeField(_("Last Modified"), auto_now=True)
    author = models.ForeignKey('Author', verbose_name=_("Author"), on_delete=models.CASCADE)
    category = models.ForeignKey('Category', verbose_name=_("Category"), on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', verbose_name=_("Tags"), blank=True)

    def get_absolute_url(self):
        return reverse('blogapp:article_details', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ['-pub_date']

    def __str__(self):
        return self.title
