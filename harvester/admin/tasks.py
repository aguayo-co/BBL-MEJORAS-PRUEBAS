"""Define admin interfaces for Harvester app."""

import logging
import os.path
from urllib.parse import urljoin

from django.core.files.storage import default_storage
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.html import format_html

from biblored.settings import MEDIA_ROOT
from harvester.helpers import send_mass_html_mail


def export_in_background(
    model_class,
    serialized_query,
    file_format,
    user,
    file_name,
    resource_class,
    absolute_uri,
):
    queryset = model_class.objects.filter(pk__gt=1000)
    queryset.query = serialized_query

    data = resource_class().export(queryset)
    export_data = file_format.export_data(data)

    file_path = os.path.join("export", file_name)
    file_mode = "wb" if file_format.is_binary() else "w"
    download_url = urljoin(absolute_uri, default_storage.url(file_path))

    # Prepare Directory
    # if not default_storage.exists(os.path.join(MEDIA_ROOT, "export")):
    #    os.mkdir(os.path.join(MEDIA_ROOT, "export"))

    # Upload file to Storage
    with default_storage.open(file_path, file_mode) as remote_file:
        remote_file.write(export_data)

    # Send Mail
    html_body = loader.render_to_string(
        "harvester/email/export_file.html",
        {
            "url": download_url,
            "file_name": file_name,
        },
    )
    plain_body = loader.render_to_string(
        "harvester/email/export_file.html",
        {
            "url": download_url,
            "file_name": file_name,
        },
    )
    send_mass_html_mail(
        (
            (
                "Archivo exportado",
                plain_body,
                html_body,
                None,
                [user.email],
            ),
        ),
        fail_silently=False,
    )
    return format_html(
        f"Archivo Disponible en <a href='{download_url}'>{file_name}</a>"
    )


def hide_show_queryset_task(queryset, action):
    """Mark given elements as visible - invisible."""
    visible = False if action == "hide" else True
    num_updated_elements = 0

    if queryset.model._meta.model_name == "datasource":
        for source in queryset:
            source.set_set.update(visible=visible, updated_at=timezone.now())
            source.contentresource_set.update(
                visible=visible, updated_at=timezone.now()
            )
            num_updated_elements += (
                source.set_set.count() + source.contentresource_set.count()
            )
    else:
        num_updated_elements += queryset.update(
            visible=visible, updated_at=timezone.now()
        )

    if queryset.model._meta.model_name == "set":
        from harvester.models import ContentResource

        content_resources = ContentResource.objects.filter(
            setandresource__set__in=queryset
        )
        num_updated_elements += content_resources.update(
            visible=visible, updated_at=timezone.now()
        )

    if visible:
        return _(f"Se han marcado {num_updated_elements} elementos como Visibles.")
    return _(f"Se han marcado {num_updated_elements} elementos como No-Visibles.")
