"""Integrate resources app with Django admin."""

from constance.admin import Config
from constance.admin import ConstanceAdmin as DefaultConstanceAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django_db_logger.admin import StatusLogAdmin as BaseStatusLogAdmin
from django_db_logger.models import LOG_LEVELS, StatusLog
from import_export import resources
from import_export.admin import ExportActionMixin
from import_export.fields import Field
from import_export.widgets import DateTimeWidget
from import_export.formats import base_formats

from .forms import ConstanceForm, StatusLogForm
from harvester.admin.mixins import ExportInBackgroundMixin


# Admin Classes
class ConstanceAdmin(DefaultConstanceAdmin):
    """Expose the Constance Admin Interface."""

    change_list_form = ConstanceForm


# Overrides Constance Config
admin.site.unregister([Config])
admin.site.register([Config], ConstanceAdmin)


class StatusLogResource(resources.ModelResource):
    """Register StatusLog for Exporting."""

    level = Field(attribute="level", column_name=_("nivel"))
    msg = Field(attribute="msg", column_name=_("evento"))
    create_datetime = Field(
        attribute="create_datetime", column_name=_("fecha"), widget=DateTimeWidget()
    )

    class Meta:
        """Set options for StatusLogResource."""

        model = StatusLog
        fields = ("id", "level", "msg", "create_datetime")
        export_order = ("id",)

    def dehydrate_level(self, obj):  # pylint: disable=no-self-use
        """Return the String representation for Log Levels."""
        return str(dict(LOG_LEVELS)[obj.level])

    def dehydrate_msg(self, obj):
        """Truncate the message to 32767 characters."""
        return f"{obj.msg[:32764]}..." if len(obj.msg) > 32767 else obj.msg


class StatusLogAdmin(ExportInBackgroundMixin, ExportActionMixin, BaseStatusLogAdmin):
    """Expose the Logging Admin Interface."""

    search_fields = ["msg", "trace"]
    list_filter = ["create_datetime", "level"]
    list_display = ("colored_msg", "create_datetime_format")
    list_per_page = 20
    fields = ["level", "msg", "trace", "create_datetime"]
    form = StatusLogForm
    resource_class = StatusLogResource
    show_change_form_export = False
    formats = (
        base_formats.CSV,
        base_formats.XLSX,
        # base_formats.TSV,
        # base_formats.ODS,
        # base_formats.JSON,
        # base_formats.YAML,
        # base_formats.HTML,
    )
    # Set translatable field names in list
    BaseStatusLogAdmin.colored_msg.short_description = _("evento")

    def create_datetime_format(self, instance):
        """Return the formatted creation datetime."""
        return instance.create_datetime

    create_datetime_format.short_description = _("fecha")

    def has_change_permission(self, request, obj=None):
        """Deny changes."""
        return False

    def has_add_permission(self, request):
        """Deny creations."""
        return False

    class Meta:
        indexes = [
            models.Index(fields=["create_datetime"]),
            models.Index(fields=["level"]),
            models.Index(fields=["msg"]),
            models.Index(fields=["trace"]),
        ]


# Overrides DBLogger Config.
admin.site.unregister(StatusLog)
admin.site.register(StatusLog, StatusLogAdmin)
