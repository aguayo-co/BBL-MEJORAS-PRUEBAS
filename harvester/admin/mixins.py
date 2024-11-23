"""Define admin interfaces for Harvester app."""

import logging

from django.conf import LazySettings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from import_export.formats.base_formats import CSV, XLS, XLSX

settings = LazySettings()

logger = logging.getLogger("")


class ExportInBackgroundMixin:
    formats = (
        CSV,
        XLSX,
    )
    show_export_button = False

    def export_admin_action(self, request, queryset):
        """
        Exports the selected rows using file_format.
        """
        export_format = request.POST.get("file_format")

        formats = self.get_export_formats()
        if (
            getattr(settings, "IMPORT_EXPORT_SKIP_ADMIN_ACTION_EXPORT_UI", False)
            is True
        ):
            file_format = formats[0]()

            # Custom QS
            if hasattr(self, "get_custom_export_queryset"):
                queryset = self.get_custom_export_queryset(queryset)

            file_name = self.get_export_filename(request, queryset, file_format)
            user = request.user
            absolute_uri = request.build_absolute_uri("/")

            async_task(
                "harvester.admin.tasks.export_in_background",
                queryset.model,
                queryset.query,
                file_format,
                user,
                file_name,
                self.resource_class,
                absolute_uri,
                group=f"Exportación en segundo plano {file_name}",
                task_name="Exportación en segundo plano de registros",
            )
            # Send user notification
            messages.add_message(
                request,
                messages.INFO,
                _(
                    f"Se ha programado la exportación del archivo solicitado, será enviado al correo electrónico registrado para el usuario {user.username}"
                ),
            )

            # post_export.send(sender=None, model=self.model)
            return HttpResponseRedirect(reverse("admin:index"))

    export_admin_action.short_description = _(
        "Exportar %(verbose_name_plural)s seleccionados en segundo plano"
    )

    actions = admin.ModelAdmin.actions + tuple([export_admin_action])
