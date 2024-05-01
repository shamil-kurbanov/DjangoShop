import csv

from django.db.models import QuerySet
from django.db.models.options import Options
from django.http import HttpRequest, HttpResponse


class ExportAsCSVMixin:
    """
    The `ExportAsCSVMixin` class provides a mixin for exporting a queryset as a CSV file.
    """

    def export_as_csv(self, request: HttpRequest, queryset: QuerySet):
        # Obtain metadata of the model
        meta: Options = self.model._meta

        # Generate a list of field names from the model metadata
        field_names = [field.name for field in meta.fields]

        # Create a HttpResponse object, which will serve as a CSV file
        response = HttpResponse(content_type="text/csv")

        # Set the content disposition to attachment, allowing the file to be downloaded
        response["Content-Disposition"] = f"attachment; filename={meta}-export.csv"

        # Initialize a CSV writer object, which will write data into the HttpResponse object
        writer = csv.writer(response)

        # Write the field names as the header row into the CSV file
        writer.writerow(field_names)

        # Iterate across every object in the queryset
        for obj in queryset:
            # Write a row into the CSV file for each object, by getting values of all fields in the object
            writer.writerow([getattr(obj, field) for field in field_names])

        # Return the HttpResponse object, which is now a CSV file populated with data
        return response

    # Provide a short description, which can be used in Django admin for labelling the action
    export_as_csv.short_description = "Export as CSV"
