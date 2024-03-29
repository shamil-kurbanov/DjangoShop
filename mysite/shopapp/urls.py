from django.urls import path

from .views import (
    ShopIndexView,
    GroupsListView,
    ProductsDetailsView,
    ProductsListView,
    OrderDetailView,
    ProductCreateView,
    ProductUpdateView,
    create_order,
    OrdersListView,
    ProductDeleteView,
    OrderUpdateView,
    OrderCreateView,
    OrderDeleteView,
    example_view,
)

app_name = "shopapp"

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductsDetailsView.as_view(), name="product_details"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/confirm-archive/", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/confirm-delete/", OrderDeleteView.as_view(), name="order_delete"),
    path('example/', example_view, name='example_url'),
]
