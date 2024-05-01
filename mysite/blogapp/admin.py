from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'author', 'category')  # Fields to display in list view
    ordering = ('-pub_date',)  # Default sorting
    search_fields = ('title', 'content',)  # Fields to search by
    list_filter = ('pub_date', 'author', 'category')  # Fields to filter by
