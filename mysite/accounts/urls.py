from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (login_view,
                    get_cookies_view,
                    set_cookies_view,
                    get_session_view,
                    set_session_view,
                    logout_view,
                    MyLogoutView,
                    AboutMeView,
                    RegisterView,
                    FooBarView,
                    UpdateProfileView,
                    UserListView,
                    UserDetailView,
                    HelloView,
                    )

app_name = 'accounts'

urlpatterns = [
    # path('login/', login_view, name='login')
    path('login/',LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True),
        name='login'
    ),
    path('logout/', logout_view, name='logout'),
    # path('logout/', MyLogoutView.as_view(), name='logout'),
    path('cookies/get/', get_cookies_view, name='cookies_get'),
    path('cookies/set/', set_cookies_view, name='cookies_set'),

    path('session/get/', get_session_view, name='session_get'),
    path('session/set/', set_session_view, name='session_set'),


    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path('update/', UpdateProfileView.as_view(), name='update_profile'),
    path('users-list/', UserListView.as_view(), name='users_list'),
    path('user-detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),

    path("hello/", HelloView.as_view(), name="hello"),
]
