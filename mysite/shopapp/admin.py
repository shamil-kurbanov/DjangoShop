import csv
from io import TextIOWrapper

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products

# Import our Product and Order models
from .models import Product, Order

# Import our mixin that allows us to export data to CSV
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


# Define a way to show orders inline in our Product admin page
class OrderInline(admin.TabularInline):
    # Linking this inline object with the ordering feature of the Product model
    model = Product.orders.through


# Define an admin action to set product to archived
@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """
        Change the archived status of selected rows.
    """
    # Set the 'archived' field of selected rows to be True
    queryset.update(archived=True)


# Define an admin action to set product to unarchived
@admin.action(description="Unarchived products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    # Set the 'archived' field of selected rows to be False
    queryset.update(archived=False)


# Define the admin interface for the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    # Define the actions that will be available in the admin interface
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",  # Add the CSV export action from our mixin
    ]

    # Defining inlines for the admin interface
    inlines = [
        OrderInline,  # Make it possible to modify the orders of products directly on product pages
    ]

    # Set which fields are displayed in the list view
    list_display = "pk", "name", "description_short", "price", "discount", "archived"

    # Specifies the fields in list_display that should link to the change page of an object
    list_display_links = "pk", "name"

    # The ordering (-field_name) indicates descending order, field_name indicates ascending order
    ordering = "-name", "pk"

    # Also search for entered terms in the Product's `name` and `description` fields
    search_fields = "name", "description"

    # Define sections of the detail view of an object, each item in fieldsets is a tuple, where the first element
    # is a name of the section
    fieldsets = [
        # The first section contains name and description fields
        (None, {
            "fields": ("name", "description"),
        }),

        # The second section "Price options" has price and discount fields.
        # It has wide and collapsed in its classes
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),

        # The third section "Extra options" contains archived filed used for soft delete.
        # It has collapsed in its classes
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        })
    ]

    # Method to shorten descriptions to first 48 characters for list display.
    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."

    change_list_template = "shopapp/products_changelist.html"

    # Method to handle importing CSV data. Presents a form asking for CSV file
    def import_csv(self, request: HttpRequest) -> HttpResponse:

        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_products(
            file = request.FILES['csv_file'],
            encoding=request.encoding,
        )
        self.message_user(request, "Successfully imported products from CSV file.")
        return redirect('..')

    # Method extends standard URL routing of Django Admin with a custom URL for CSV importing
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import-product-csv/", self.import_csv, name="import_products_csv"),
        ]
        return new_urls + urls





# Define a way to show products inline in our Order admin page
class ProductInline(admin.StackedInline):
    # Linking this inline object with the ordering feature of the Order model
    model = Order.products.through


# Define the admin interface for the Order model


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Defining inlines for the admin interface
    inlines = [
        ProductInline,  # Make it possible to modify the products of orders directly on order pages
    ]

    # Set which fields are displayed in the list view
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    # Overrides the get_queryset method for a custom one to improve performance
    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    # Presents a user's first name or username in the list view
    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
