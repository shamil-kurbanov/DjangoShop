from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View

from .forms import ProductForm, OrderForm
from .models import Product, Order

from .forms import GroupForm


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
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
    template_name = 'shopapp/products-list.html'
    # def get_context_data(self, **kwargs):
    # context = super().get_context_data(**kwargs)
    # context['products'] = Product.objects.all()
    # return context
    # model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'price', 'description', 'discount']
    success_url = reverse_lazy('shopapp:products_list')


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'price', 'description', 'discount']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:product_details', kwargs={'pk': self.object.pk},
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


def create_product(request: HttpRequest) -> HttpResponse:
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


class OrderUpdateView(UpdateView):
    template_name_suffix = '_update_form'
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'order'
    fields = ['user', 'promocode', 'delivery_address', 'products']

    def get_success_url(self):
        return reverse('shopapp:order_details', kwargs={'pk': self.object.pk})

class OrdersListView(ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'orders'


class OrderDetailView(DetailView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    context_object_name = 'order'


class OrderCreateView(CreateView):
    model = Order
    fields = ['user', 'promocode', 'products', 'delivery_address']
    success_url = reverse_lazy('shopapp:orders_list')

class OrderDeleteView(DeleteView):
    model = Order
    success_url ='shopapp:orders_list'
    success_message = 'Order deleted'
    def get_success_url(self):
        return reverse_lazy('shopapp:orders_list')