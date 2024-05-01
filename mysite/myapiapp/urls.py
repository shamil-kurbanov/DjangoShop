from django.urls import path

from .views import (hello_world_view,
                    GroupsListView,
                    BookListCreate,
                    BookRetrieveUpdateDestroy,
                    UsersListView,
                    UserRetrieveUpdateDestroy,
                    GroupRetrieveUpdateDestroy
                    )

from shopapp.views import (
                    ProductsListAPIView,
                    ProductRetrieveUpdateDestroyAPIView,
                    OrdersListViewAPIView,
                    OrderRetrieveUpdateDestroyAPIView)

app_name = "myapiapp"

urlpatterns = [
    path("hello/", hello_world_view, name="hello"),

    path("groups/", GroupsListView.as_view(), name="groups"),
    path('groups/<int:pk>/', GroupRetrieveUpdateDestroy.as_view(), name='group-detail'),

    path('books/', BookListCreate.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroy.as_view(), name='book-detail'),

    path('users/', UsersListView.as_view(), name='users'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroy.as_view(), name='user-detail'),

    path('products/', ProductsListAPIView.as_view(), name='products'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-detail'),

    path('orders/', OrdersListViewAPIView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderRetrieveUpdateDestroyAPIView.as_view(), name='order-detail'),
]
