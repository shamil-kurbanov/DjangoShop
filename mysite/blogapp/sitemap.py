from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article  # assuming BlogPost is the model you want to include in the sitemap


class BlogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        # return all published blog posts
        return Article.objects.filter(pub_date__isnull=False).order_by('-pub_date')

    def lastmod(self, obj: Article):
        return obj.pub_date

    def location(self, item: Article):
        # return the url for each article
        return item.get_absolute_url()