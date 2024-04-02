from django.urls import path, include

from accounts.views import UserListView
from .views import login_view

app_name = 'myauth'


urlpatterns = [
    path('login/', login_view, name='login'),
    ]