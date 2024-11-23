"""Define Forms for resources app."""
import os

from constance.admin import ConstanceForm as DefaultConstanceForm
from constance.admin import config
from django import forms
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models.query import EmptyQuerySet
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django_db_logger.models import StatusLog


class ConstanceForm(DefaultConstanceForm):
    """Custom Form for Constance Config Administration."""

    def save(self):
        """Save uploaded files in a custom location and save the config data."""
        for file_field in self.files:
            prev_file_path = getattr(config, file_field)
            new_file = self.cleaned_data[file_field]
            new_file_path = os.path.join(settings.CONSTANCE_UPLOAD_PATH, new_file.name)
            self.cleaned_data[file_field] = default_storage.save(
                new_file_path, new_file
            )
            # Delete Previous File after new is saved
            if prev_file_path and self.cleaned_data[file_field] != prev_file_path:
                default_storage.delete(prev_file_path)

        # Clear files array to avoid duplicate saving.
        self.files = []
        super().save()


class StatusLogForm(ModelForm):
    """Translatable form for the StatusLog model."""

    class Meta:
        """Define translatable field's labels."""

        model = StatusLog
        fields = "__all__"
        labels = {
            "level": _("nivel"),
            "msg": _("evento"),
            "trace": _("traza"),
            "create_datetime": _("fecha"),
        }


class FiltersForm(forms.Form):
    """
    Mixin for Filter forms.

    Applies filter() to a queryset based on the form fields.

    `FIELDS_LOOKUPS` must be a dictionary with the lookup for each form field.

    Example:
    ```
    FIELDS_LOOKUPS = {
        "field_name": "lookup",
        "name": "name__iexact",
    }
    ```

    """

    FIELDS_LOOKUPS = None
    # Order by is added to allow order_by query parameter to
    # be kept when submiting the form.
    # It will be ignored when applying filters.
    order_by = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, queryset, *args, **kwargs):
        """Initialize form and set initial queryset."""
        self.queryset = queryset
        super().__init__(*args, **kwargs)

    def filtered_queryset(self):
        """Apply valid filters to queryset."""
        if self.is_valid():

            filters = {}
            for field, value in self.cleaned_data.items():
                if (
                    field == "order_by"
                    or value in self.fields[field].empty_values
                    or isinstance(value, EmptyQuerySet)
                ):
                    continue

                filters[
                    self.FIELDS_LOOKUPS[field]  # pylint: disable=unsubscriptable-object
                ] = value

            if filters:
                self.queryset = self.queryset.filter(**filters)

            return self.queryset

        return self.queryset.none()
