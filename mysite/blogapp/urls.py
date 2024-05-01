from django.urls import path
from django.contrib.auth.views import LoginView

from .views import (ArticlesListView,
                    ArticleDetailView,
                    ArticleCreateView,
                    CreateUserView,
                    ArticleUpdateView,
                    ArticleDeleteView,
                    LatestArticlesFeed
                    )

app_name = 'blogapp'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('articles/', ArticlesListView.as_view(), name='articles'),
    path('articles/<int:pk>', ArticleDetailView.as_view(), name='article_details'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('article/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),

    # pk is the model object's primary key
    path('articles/new/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/latest/feed/', LatestArticlesFeed(), name='articles_feed'),
    path("register/", CreateUserView.as_view(), name="register"),
]