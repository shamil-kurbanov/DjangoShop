import csv
import logging
from timeit import default_timer

from attr import field
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.models import Group
from django.http import (HttpResponse,
                         HttpRequest,
                         HttpResponseRedirect,
                         HttpResponseForbidden)
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (TemplateView,
                                  ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from django.views import View
from rest_framework.decorators import action

from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, decorators, permissions, status, viewsets
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import ProductSerializer, OrderSerializer

from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order

from .common import save_csv_products

log = logging.getLogger(__name__)



class ShopIndexView(View):
    """
    A class-based view for rendering the shop index page.

    Methods:
    - get(request: HttpRequest) -> HttpResponse: Renders the shop index page.

    """
    @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": len(Product.objects.all())
        }
        log.debug('Products for shop index: %s', products)
        log.info("Rendering shop index page")

        print('shop index context', context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    """
    GroupsListView

    A class-based view for displaying a list of groups.

    Methods:
        - get(request: HttpRequest) -> HttpResponse
        - post(request: HttpRequest) -> HttpResponse

    Attributes:
        - None

    Methods:
        - get(request: HttpRequest) -> HttpResponse:
            Displays the groups list page with a form and a list of groups.

            Parameters:
                - request (HttpRequest): The HTTP request object.

            Returns:
                - HttpResponse: The rendered HTTP response with the groups list page.

        - post(request: HttpRequest) -> HttpResponse:
            Handles the submission of the group form.

            Parameters:
                - request (HttpRequest): The HTTP request object.

            Returns:
                - HttpResponse: The redirect response to the current URL.

    Example usage:
    ```python
    # Create an instance of the GroupsListView
    groups_list_view = GroupsListView()

    # Call the get() method
    response = groups_list_view.get(request)

    # Call the post() method
    response = groups_list_view.post(request)
    ```
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductsDetailsView(DetailView):
    """
    The ProductsDetailsView class is a subclass of the DetailView class in Django.
    It is used to retrieve and display details of a specific Product object from the database.

    Attributes:
        - template_name (str): The name of the HTML template file to be used for rendering the view.
        - model (Model): The model class representing the Product object.
        - context_object_name (str): The name of the variable that will be used
          to access the Product object in the template.

    Methods:
        - get(self, request: HttpRequest, pk: int) -> HttpResponse:
            Retrieves the Product object with the given primary key (pk) from the database and renders
            the template with the retrieved object as the context.

            Parameters:
                - request (HttpRequest): The request object received from the client.
                - pk (int): The primary key of the Product object to be retrieved.

            Returns:
                - HttpResponse: The rendered HTML response containing the product details.

    """
    template_name = 'shopapp/product-details.html'
    model = Product
    context_object_name = "product"

    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    # product = get_object_or_404(Product, pk=pk)
    # context = {
    #     "product": product
    # }
    # return render(request, 'shopapp/product-details.html', context=context)


class ProductsListView(ListView):
    """

    :class: ProductsListView

    A class that displays a list of products.

    Attributes:
    ----------
    - ``template_name``: (`str`) The template name for rendering the products list.
        Default is 'shopapp/products-list.html'.
    - ``context_object_name``: (`str`) The name of the variable to be used in the template for the list of products.
        Default is 'products'.
    - ``queryset``: (`QuerySet`) The queryset of products to be used for displaying the list. By default, it filters
        Product objects where archived=False.

    """
    template_name = 'shopapp/products-list.html'
    # def get_context_data(self, **kwargs):
    # context = super().get_context_data(**kwargs)
    # context['products'] = Product.objects.all()
    # return context
    # model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    """

    :class: ProductCreateView

    A class-based view for creating a new product in the shop application.

    Attributes:
        - model: The model class that the view is associated with (Product)
        - fields: The fields of the model that should be included in
                the form (name, price, description, discount, preview)
        - success_url: The URL to redirect to after successfully
                creating the product (reverse_lazy('shopapp:products_list'))

    Methods:
        - test_func(): Checks if the user is a superuser or has the permission to create a product.
          Returns True if the user is authorized, False otherwise.
        - form_valid(form): Overrides the form_valid method of CreateView. Sets the 'created_by' attribute of
          the form instance to the current user and calls the base implementation of form_valid.

    """

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.has_perm('shopapp.can_create_product')

    model = Product
    fields = ['name', 'price', 'description', 'discount', 'preview']
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    """
    ProductUpdateView class is a view that allows users to update a product. It inherits from Django's UpdateView class.

    Attributes:
        - model (class attribute): The model class that the view will be based on.
          In this case, it is the Product model.
        - fields (class attribute): The fields of the model that will be editable in the update form.
        - template_name_suffix (class attribute): The suffix to append to the template name for
          rendering the update form.

    Methods:
        - test_func(): Checks if the user has permission to edit this product. Returns True if the user is a superuser
          or if they have the 'shopapp.change_product' permission and they are the author of the product.
          Returns False otherwise.
        - dispatch(request, *args, **kwargs): Overrides the dispatch method of the parent class.
          If the user does not have permission to edit this product, it returns an HttpResponseForbidden with an
          error message. Otherwise, it calls the dispatch method of the parent class.
        - get_success_url(): Returns the URL to redirect to after a successful update. The URL is generated using
          the 'shopapp:product_details' URL pattern and includes the primary key of the updated object.
    """
    model = Product
    fields = ['name', 'price', 'description', 'discount', 'preview']
    template_name_suffix = '_update_form'

    def test_func(self):
        # Check if the user is a superuser
        if self.request.user.is_superuser:
            return True
        # Check if the user has permission to edit
        elif self.request.user.has_perm('shopapp.change_product'):
            # Check if the user is the author of the product
            product = self.get_object()
            return product.created_by == self.request.user
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            return HttpResponseForbidden("You do not have permission to edit this product.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'shopapp:product_details', kwargs={'pk': self.object.pk},
        )


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    """
    ProductDeleteView

    This class is a view for deleting a product instance. It inherits from the PermissionRequiredMixin and
    DeleteView classes.

    Attributes:
        - model: The model used for the view (Product).
        - success_url: The URL to redirect to after successfully deleting
          a product (reverse_lazy('shopapp:products_list')).

    Methods:
        - test_func(self): A method that checks if the user is a superuser or has permission to delete a product.
            Returns:
                - True if the user is a superuser or has permission to delete a product.
                - False otherwise.

        - dispatch(self, request, *args, **kwargs): Overrides the default dispatch method to check permissions before
          dispatching the view.
            Parameters:
                - request: The request object.
            Returns:
                - HttpResponseForbidden: If the user does not have permission to delete the product.
                - super().dispatch(request, *args, **kwargs): If the user has permission, it dispatches the view.

        - form_valid(self, form): Overrides the default form_valid method to set the archived attribute of the product
          to True before saving.
            Parameters:
                - form: The valid form object sent to the view.
            Returns:
                - HttpResponseRedirect: Redirects to the success_url after saving the product.

    """

    def test_func(self):
        return self.request.user.is_superuser

    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def test_func(self):
        # Check if the user is a superuser
        if self.request.user.is_superuser:
            return True
        # Check if the user has permission to delete
        return self.request.user.has_perm('shopapp.delete_product')

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            return HttpResponseForbidden("You do not have permission to delete this product.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


def create_product(request: HttpRequest) -> HttpResponse:
    """
    :param request: The HTTP request object.
    :return: The HTTP response object.

    This method is used to create a new product. It takes an `HttpRequest` object as input and
    returns an `HttpResponse` object.

    If the request method is 'POST', it creates a new `ProductForm` instance with the data from the request's POST data.
     It then checks if the form is valid. If the form is valid, it saves the form, redirects the user to the list
     of products page, and returns an HTTP response with the redirect URL.

    If the request method is not 'POST', it creates a new `ProductForm` instance without any initial data.

    Finally, it renders the 'shopapp/create-product.html' template with the form as the context and returns the
    rendered HTML as the HTTP response.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse('shopapp:products_list')
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        'form': form,
    }
    return render(request, 'shopapp/create-product.html', context=context)


# def orders_list(request: HttpRequest):
#    context = {
#        "orders": Order.objects.select_related("user").prefetch_related("products").all(),
#   }
#    return render(request, 'shopapp/orders-list.html', context=context)


def create_order(request: HttpRequest) -> HttpResponse:
    """
    Create an order.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The HTTP response object.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            url = reverse('shopapp:orders_list')
            return redirect(url)
    else:
        form = OrderForm()
    context = {
        'form': form,
    }
    return render(request, 'shopapp/create-order.html', context=context)


class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Handles updating orders and provides form for update input.

    """
    template_name_suffix = '_update_form'  # Suffix for template name

    # Query for retrieving order data with related user from the database
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'order'
    # Fields to be displayed in update form
    fields = ['user', 'promocode', 'delivery_address', 'products']

    def get_success_url(self):
        """
        Returns the URL to redirect to after successful form submission.

        """
        return reverse('shopapp:order_details', kwargs={'pk': self.object.pk})


class OrdersListView(LoginRequiredMixin, ListView):
    """
    ListView subclass that displays a list of orders.

    This view requires the user to be logged in. It retrieves the orders from the database and renders them using
    a template.

    Inherits from:
        - LoginRequiredMixin: Ensures that the user is authenticated before accessing the view.
        - ListView: Provides the functionality to display a list of objects.

    Attributes:
        - queryset (QuerySet): A QuerySet of orders, including related user and products.
        - context_object_name (str): The name of the variable to use in the template when rendering the list of orders.

    Example usage:
        Create a URL pattern in your application's `urls.py` file:

        ```python
        from myapp.views import OrdersListView

        urlpatterns = [
            path('orders/', OrdersListView.as_view(), name='orders-list'),
        ]
        ```

        Then, create a template to display the orders:

        ```html
        <!-- myapp/orders_list.html -->
        <h1>Orders</h1>
        <ul>
            {% for order in orders %}
                <li>{{ order.id }} - {{ order.user.username }}</li>
            {% endfor %}
        </ul>
        ```
    """
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'orders'


class OrderDetailView(DetailView):
    """
    This class represents a detail view for an order.

    .. rubric:: Class Attributes

    - ``permission_required`` (*str*): The permission required to view the order.
    - ``queryset`` (*QuerySet*): The queryset used to retrieve the order data. It includes a select_related to
    fetch the related user and a prefetch_related to fetch the related products.
    - ``context_object_name`` (*str*): The name used to refer to the order object in the context.

    .. rubric:: Usage

    Instantiate an instance of ``OrderDetailView`` and specify the necessary attributes to customize
    the behavior of the view.

    Example:

    ```
    from django.views.generic import DetailView

    class MyOrderDetailView(OrderDetailView):
        permission_required = 'my_custom_permission'
        queryset = Order.objects.select_related("user")
        context_object_name = 'my_order'
    ```

    .. note::
        This class assumes that the necessary Django models, views, and permissions are properly set up in the project.

    """
    permission_required = 'view_order'
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'order'


class OrderCreateView(CreateView):
    """
    A class-based view for creating new orders.

    Inherits from django.views.generic.edit.CreateView.

    :ivar model: The model class used for this view (Order).
    :vartype model: django.db.models.Model
    :ivar fields: The fields of the model that will be displayed in the order creation form.
    :vartype fields: list[str]
    :ivar success_url: The URL where the user will be redirected after successfully creating the order.
    :vartype success_url: django.urls.reverse_lazy
    """
    model = Order
    fields = ['user', 'promocode', 'products', 'delivery_address']
    success_url = reverse_lazy('shopapp:orders_list')


class OrderDeleteView(DeleteView):
    """
    A class-based view for deleting an Order.

    Inherits from DeleteView class.

    Attributes:
        model (Model): The model class for which the view will delete an instance.
        success_url (str): The URL to redirect to after a successful deletion.
        success_message (str): The success message to display after a successful deletion.

    Methods:
        get_success_url(): Returns the success URL for the view.

    """
    model = Order
    success_url = 'shopapp:orders_list'
    success_message = 'Order deleted'

    def get_success_url(self):
        return reverse_lazy('shopapp:orders_list')


def example_view(request):
    """
    :param request: The HTTP request object.
    :return: An `HttpResponse` object containing the text "This is an example view."
    """
    return HttpResponse("This is an example view.")


# ----------- ViewSet ---------------------------
@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    A viewset for handling CRUD operations on the Product model.

    Inherits:
    - ModelViewSet from rest_framework.viewsets

    Attributes:
    - queryset: All products in the database. (QuerySet)
    - serializer_class: Serializer for the Product model. (Serializer)
    - filter_backends: List of filter backends used for filtering the queryset.
      Includes SearchFilter, DjangoFilterBackend, and OrderingFilter. (list)
    - search_fields: Fields used for searching products. (list)
    - filterset_fields: Fields used for filtering products. (list)
    - ordering_fields: Fields used for ordering products. (list)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['name', 'description']
    filterset_fields = ['name', 'price', 'description', 'discount', 'archived']
    ordering_fields = ['name', 'price', 'description']

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieve **product**, returns 404 if not found.",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by ID not found.")
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print('Hello products list')
        return super().list(*args, **kwargs)

    @action(detail=False, methods=["GET"])
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
            # response is a file

        return response

    @action(detail=False, methods=["POST"], parser_classes=[MultiPartParser], )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            endcoding=request.encoding,
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    """

    .. module:: order.views
       :synopsis: Order viewset module.

    .. moduleauthor:: John Doe <john.doe@example.com>

    .. versionadded:: 1.0

    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['name', 'delivery_address', 'products']
    filterset_fields = ['user', 'promocode', 'products', 'delivery_address']
    ordering_fields = ['name']


# ------------End ViewSet -----------------------


class ProductsListAPIView(ListCreateAPIView):
    """

    ProductsListAPIView

    A class-based view for listing and creating products.

    Attributes:
        queryset (QuerySet): The queryset of all products.
        serializer_class (Serializer): The serializer class for converting products to JSON.

    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    ProductRetrieveUpdateDestroyAPIView Class
    ========================================

    This class is a generic view class that provides retrieve, update, and destroy functionality for a Product object.
    It is inherited from the `generics.RetrieveUpdateDestroyAPIView` class.

    Attributes:
    -----------
    - `queryset`: A queryset that specifies the set of Product objects to be retrieved, updated, or destroyed.
    By default, it fetches all Product objects from the database.
    - `serializer_class`: The serializer class to be used for serializing and deserializing the Product objects.

    Usage:
    ------
    1. Instantiate the ProductRetrieveUpdateDestroyAPIView class with the desired arguments.
    2. Make requests to the endpoints associated with this view class to retrieve, update, or destroy Product objects.

    Example:
    --------
    from rest_framework import generics

    class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
        queryset = Product.objects.all()
        serializer_class = ProductSerializer

    Note:
    -----
    Make sure to set the `queryset` and `serializer_class` attributes appropriately before using this class.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrdersListViewAPIView(ListCreateAPIView):
    """
    A view to list and create orders.

    Inherits from `ListCreateAPIView` which is a generic view that provides
    the functionality to list and create objects.

    Attributes:
        queryset (QuerySet): The queryset that defines the list of orders
            to be displayed.
        serializer_class (Serializer): The serializer class used to
            serialize and deserialize the order objects.

    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update and destroy an order.

    Inherits from generics.RetrieveUpdateDestroyAPIView.

    Attributes:
        queryset (QuerySet): A queryset of Order objects.
        serializer_class (Serializer): The serializer class to use for the Order objects.

    Methods:
        get_object(self): Retrieves the order object based on the lookup field.
        get(self, request, *args, **kwargs): Handles GET requests.
        update(self, request, *args, **kwargs): Handles PUT requests.
        partial_update(self, request, *args, **kwargs): Handles PATCH requests.
        destroy(self, request, *args, **kwargs): Handles DELETE requests.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
