"""Define tasks to be executed periodically."""

import datetime
import logging
import os

import certifi
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Min
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.models import Schedule

from wagtail.search.backends import get_search_backend

from biblored.settings import INDEX_CHUNK_SIZE
from resources.helpers import unparallel

from .models import (
    Collection,
    ContentResource,
    ContentResourceEquivalence,
    InvalidModelInstance,
    Set,
    SetAndResource,
)

logger = logging.getLogger("biblored")  # pylint: disable=invalid-name


def schedule_cached_field_update_task(limit=5000, minutes=5):
    """Schedule the next cached field's update task."""
    func = "harvester.tasks.update_cached_fields_task"
    Schedule.objects.update_or_create(
        name=func,
        next_run=(timezone.now() + datetime.timedelta(minutes=minutes)),
        defaults={
            "name": _("Actualización de Campos Cacheados"),
            "kwargs": {"limit": limit},
            "func": func,
            "minutes": minutes,
            "schedule_type": "I",
        },
    )


@unparallel
def update_cached_fields_task(limit):
    """Call all the cached field tasks."""
    models_to_update = [Set, Collection, ContentResource, ContentResourceEquivalence]
    results = {}
    for model_to_update in models_to_update:
        results[model_to_update._meta.model_name] = update_model_cached_fields(
            limit=limit, model_class=model_to_update
        )
    return results


def update_model_cached_fields(limit, model_class):
    """Check for expired cached fields in Resource and update them."""
    instances = model_class.get_expired_instances()[:limit]
    updated_instances = []
    updated_fields = model_class.get_updated_cached_fields()

    deleted_ids = []
    for instance in instances.iterator():
        try:
            instance.update_expired_fields()
        except InvalidModelInstance:
            deleted_ids.append(instance.pk)
            instance.to_delete = True
        else:
            instance.updated_at = timezone.now()
        finally:
            updated_instances.append(instance)

            if len(updated_instances) >= settings.TASK_PAGE_LENGTH:
                model_class.objects.bulk_update(updated_instances, updated_fields)
                updated_instances.clear()

    if updated_instances:
        model_class.objects.bulk_update(updated_instances, updated_fields)

    if deleted_ids:
        logger.info(
            "No se han podido actualizar Campos Cacheados en %d %s (%s)",
            len(deleted_ids),
            model_class._meta.verbose_name_plural,
            ", ".join(str(i) for i in deleted_ids),
        )
    return f"Actualización de campos cacheados [{model_class._meta.model_name}]: ~{len(updated_instances)}, -{len(deleted_ids)}"


def schedule_delete_duplicate_resources(limit=20000, minutes=20):
    """Schedule the next cached field's update task."""
    func = "harvester.tasks.delete_duplicate_resources"
    Schedule.objects.update_or_create(
        name=func,
        next_run=(timezone.now() + datetime.timedelta(minutes=minutes)),
        defaults={
            "name": _("Borrado de Registros Duplicados"),
            "kwargs": {"limit": limit},
            "func": func,
            "minutes": minutes,
            "schedule_type": "I",
        },
    )


@unparallel
def delete_duplicate_resources(limit):
    """Delete duplicate resources from each DatSource."""
    deleted = []
    try:
        filter_query = (
            ContentResource.objects.exclude(
                ContentResource.get_cached_field_expired_filters("dynamic_identifier")
            )
            .values("dynamic_identifier_cached", "data_source")
            .order_by()
            # Min() is not very efficient in PostgreSQL :(.
            .annotate(Count("id"), Min("id"))
            .filter(id__count__gt=1)
        )

        resources = ContentResource.objects.filter(
            dynamic_identifier_cached__in=filter_query.values(
                "dynamic_identifier_cached"
            )
        ).exclude(id__in=filter_query.values("id__min"))[:limit]

        for resource in resources.iterator():
            deleted.append(
                f"{resource.pk}: "
                f"{resource.data_source_id}-{resource.dynamic_identifier_cached}"
            )
            resource.to_delete = True
            resource.save()

        if deleted:
            logger.info(
                "%d recursos duplicados marcados para eliminar en segundo plano (%s)",
                len(deleted),
                ", ".join(deleted),
            )
    finally:
        return f"{len(deleted)} Recursos duplicados marcados para eliminar en segundo plano"


def update_certs():
    """Install Certificates for Digicert."""
    cafile = certifi.where()
    with open(cafile, "ab") as outfile:
        for root, __, files in os.walk("certificates"):
            count = len(files)
            for file in files:
                with open(os.path.join(root, file), "rb") as infile:
                    customca = infile.read()
                    outfile.write(customca)
    return f"{count} Certificates Installed"


def mass_change_resource_set_task(resources_id_list, data_source_id, new_set):
    """Mass change a :ContentResource: object related `Set` in background."""
    backend = get_search_backend("default")
    search_index = backend.get_index_for_model(ContentResource)
    object_list = ContentResource.objects.filter(id__in=resources_id_list)
    resources_to_index = []
    setandresource_to_update = []
    updated_objects = 0
    index_chunk_size = INDEX_CHUNK_SIZE

    # Change Set
    logger.info("Starting Change Set")
    set_and_resources = SetAndResource.objects.filter(
        set__data_source_id=data_source_id, resource_id__in=resources_id_list
    )
    with transaction.atomic():
        # Prevent duplicates
        set_and_resources.filter(set=new_set).delete()

        for set_and_resource in set_and_resources.iterator():
            set_and_resource.set = new_set
            set_and_resource.updated_at = timezone.now()
            setandresource_to_update.append(set_and_resource)
            if len(setandresource_to_update) >= index_chunk_size:
                SetAndResource.objects.bulk_update(
                    setandresource_to_update, ["set", "updated_at"]
                )
                setandresource_to_update.clear()
        SetAndResource.objects.bulk_update(
            setandresource_to_update, ["set", "updated_at"]
        )

        # Mark Resources as updated and
        # Indexing: Bulk indexing
        logger.info("Starting Marking ContentResources as Updated")
        for content_resource in object_list.iterator():
            content_resource.updated_at = timezone.now()
            resources_to_index.append(content_resource)

            if len(resources_to_index) >= index_chunk_size:
                logger.info("Starting Indexing of changed ContentResources")
                updated_objects += ContentResource.objects.bulk_update(
                    resources_to_index, ["updated_at"]
                )
                search_index.add_items(ContentResource, resources_to_index)
                resources_to_index.clear()

        updated_objects += ContentResource.objects.bulk_update(
            resources_to_index, ["updated_at"]
        )
        search_index.add_items(ContentResource, resources_to_index)

    return f"Asignados correctamente {updated_objects} Recursos a la Colección Institucional '{new_set}'"
