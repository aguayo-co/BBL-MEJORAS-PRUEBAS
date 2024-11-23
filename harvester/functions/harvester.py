"""Define functions to execute harvesting tasks."""

import datetime
import logging
import mimetypes
import os
import tempfile
import urllib
import uuid

from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task, fetch_group, schedule
from psycopg2 import DataError, IntegrityError
from pyunpack import Archive
from wagtail.search.backends import get_search_backend
from wagtail.search.index import insert_or_update_object

from biblored.settings import INDEX_CHUNK_SIZE
from ..models import (
    LONG_TEXT,
    ContentResource,
    ContentResourceEquivalence,
    CreatorEquivalenceRelation,
    DataSource,
    InvalidModelInstance,
    LanguageEquivalenceRelation,
    RightsEquivalenceRelation,
    Set,
    SetAndResource,
    SubjectEquivalenceRelation,
    TypeEquivalenceRelation,
    ControlHarvestStatus,
)

bbl_logger = logging.getLogger("biblored")  # pylint: disable=invalid-name
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class BadSource(Exception):
    """General error for when the source fails and is invalid."""


MAPPABLE_FIELDS = [
    "abstract",
    "accessRights",
    "accrualMethod",
    "accrualPeriodicity",
    "accrualPolicy",
    "alternative",
    "audience",
    "available",
    "bibliographicCitation",
    "conformsTo",
    "contributor",
    "coverage",
    "created",
    "creator",
    "date",
    "dateAccepted",
    "dateCopyrighted",
    "dateSubmitted",
    "description",
    "educationLevel",
    "extent",
    "format",
    "hasFormat",
    "hasPart",
    "hasVersion",
    "identifier",
    "instructionalMethod",
    "isFormatOf",
    "isPartOf",
    "isReferencedBy",
    "isReplacedBy",
    "isRequiredBy",
    "issued",
    "isVersionOf",
    "license",
    "mediator",
    "medium",
    "modified",
    "provenance",
    "publisher",
    "references",
    "relation",
    "replaces",
    "requires",
    "rightsHolder",
    "source",
    "spatial",
    "tableOfContents",
    "temporal",
    "title",
    "topographicNumber",
    "valid",
    "type",
    "subject",
    "rights",
    "language",
]


def generate_file_name(extension):
    """Generate a unique filename."""
    return "%(random)s.%(ext)s" % {"random": uuid.uuid1(), "ext": extension.strip(" .")}


def get_sets(data_source):
    """
    Return the list of sets for the provided source.

    If the source does not support sets, a generic one is returned.
    """
    source_format = data_source.config["format"]

    if source_format == "oai_dc":
        from .oai import get_sets_oai

        return get_sets_oai(data_source)

    return [
        (
            f"set_ds_{data_source.id}",
            f"Generated Set for Data Source: {data_source.name}",
        )
    ]


def get_harvested_sets(data_source):
    """Return the list of sets that have been harvested previously."""
    return Set.objects.filter(data_source=data_source).values_list("spec", flat=True)


def get_mapping(form_list):
    """Generate the mapping information."""
    mapping = {"positions": {}}
    for form in form_list:
        if "csv_mapping" in form.cleaned_data:
            for file_field, m_field in form.cleaned_data.items():
                if m_field in MAPPABLE_FIELDS:
                    if m_field not in mapping:
                        mapping[m_field] = []
                    mapping[m_field].append(file_field)
        else:
            for m_field in MAPPABLE_FIELDS:
                if m_field in form.cleaned_data:
                    if m_field not in mapping:
                        mapping[m_field] = []
                    mapping[m_field].append(form.cleaned_data[m_field])
        # Positions
        for m_field in MAPPABLE_FIELDS:
            if f"position_{m_field}" in form.cleaned_data:
                if m_field not in mapping["positions"]:
                    mapping["positions"][m_field] = (
                        form.cleaned_data[f"position_{m_field}"] - 1
                    )
    return mapping


def decompress(file_path, extract_to):
    """
    Extract a compressed file and return the list of the uncompressed paths.

    Accepts 7z, rar and zip files.
    """
    bbl_logger.info(_("Descomprimiendo archivo en: %(path)s"), {"path": extract_to})
    if not os.path.isdir(extract_to):
        os.makedirs(extract_to)

    Archive(file_path).extractall(extract_to)
    # Get the decompressed urls
    files_paths = []
    for root, __, files in os.walk(extract_to):
        for file in files:
            files_paths.append(os.path.join(root, file))

    return files_paths


def get_storage_path(data_source_id, group_id):
    """Return a path to be used for files of the provided source and uuid."""
    time = datetime.datetime(1582, 10, 15) + datetime.timedelta(
        microseconds=uuid.UUID(group_id).time // 10
    )
    date = str(time.strftime("%Y-%m-%d"))
    return os.path.join("harvester", str(data_source_id), date, str(group_id))


def make_local_path(storage_path):
    """Create a temporary directory matching a storage path."""
    local_path = os.path.join(tempfile.gettempdir(), storage_path)
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    return local_path


def download_file_and_upload(url, datasource, group_id, user):
    """
    Get the files to process ready for usage.

    Returns a list of file paths to use for data processing.
    """
    datasource_id = datasource.id
    bbl_logger.info(_("Descargando archivo desde: %(url)s"), {"url": url})

    try:

        harvest_stage = ControlHarvestStatus(
            data_source=datasource, group_id=group_id, user=user, stage=2, status=1
        )
        harvest_stage.change_stage_by_step()

        local_file, headers = urllib.request.urlretrieve(url)

        if local_file:
            harvest_stage.stage = 3
            harvest_stage.status = 1
            bbl_logger.info(
                _("Archivo descargado correctamente: %(url)s"), {"url": url}
            )
        else:
            harvest_stage.stage = 4
            harvest_stage.status = 2
            bbl_logger.warning(_("Archivo no descargado: %(url)s"), {"url": url})

        harvest_stage.change_stage_by_step()

        # Get file extension
        mimetypes.add_type("application/x-7z-compressed", "7z")
        mimetypes.add_type("application/x-zip-compressed", "zip")
        mimetypes.add_type("application/x-rar-compressed", "rar")
        mimetypes.add_type("application/octet-stream", "zip")
        mimetypes.add_type("application/zip", "zip")
        mimetypes.add_type("application/marc", "mrc")
        extension = mimetypes.guess_extension(headers.get("content-type"))

        datasource = DataSource.objects.get(id=datasource_id)
        if datasource.config["format"] == "csv":
            extension = ".csv"

        # Decompress File if apply
        storage_path = get_storage_path(datasource_id, group_id)
        local_path = make_local_path(storage_path)

        # Decompress File
        if extension in [".7z", ".zip", ".rar"]:
            files_to_upload = decompress(local_file, local_path)
        else:
            files_to_upload = [local_file]

        if not extension:
            extension = ".tmp"

        # Normalize file names
        bbl_logger.info(_("Guardando archivo en: %(path)s"), {"path": storage_path})
        harvest_stage.stage = 5
        harvest_stage.status = 1
        harvest_stage.change_stage_by_step()

        uploaded_files = []
        for file_to_upload in files_to_upload:
            # Get file extension
            file_extension = os.path.splitext(file_to_upload)[1]
            if not file_extension:
                file_extension = extension

            # Move files to a valid location
            new_local_file = os.path.join(
                local_path, generate_file_name(file_extension)
            )
            os.rename(file_to_upload, new_local_file)

            # Upload to storage
            file_storage_path = new_local_file.replace(
                tempfile.gettempdir(), ""
            ).lstrip(os.sep)
            upload_to_storage(file_storage_path, new_local_file)
            uploaded_files.append(file_storage_path)

            return uploaded_files

    except Exception as e:
        harvest_stage.status = 2
        harvest_stage.change_stage_by_step()
        return []


def prepare_file(storage_path):
    """Get the file and make a local copy for quick access."""
    local_path = os.path.join(tempfile.gettempdir(), storage_path.lstrip(os.sep))
    file_in_local = os.path.exists(local_path)
    if not file_in_local:
        save_file_on_local(storage_path)
    return open(local_path, "rb")


def save_file_on_local(storage_path):
    """Store file on temporary directory for quick access."""
    local_path = os.path.join(tempfile.gettempdir(), storage_path.lstrip(os.sep))
    local_root = os.path.split(local_path)
    os.makedirs(local_root[0], exist_ok=True)
    with default_storage.open(storage_path, "rb") as remote_file, open(
        local_path, "wb+"
    ) as local_file:
        local_file.write(remote_file.read())
    return True


def upload_to_storage(storage_path, local_path):
    """Save file to default storage."""
    with open(local_path, "rb") as local_file:
        default_storage.save(storage_path, File(local_file))
    return True


def log_results_task(group_id, set_name, source_name):
    """Schedule a task to log results of a harvesting group."""
    schedule(
        "harvester.functions.harvester.log_results",
        group_id,
        set_name,
        source_name,
        next_run=(timezone.now() + datetime.timedelta(seconds=10)),
    )


def log_results(group_id, set_name, source_name):
    """Log the results of a harvesting group."""
    results = {
        "success": {"updated": 0, "created": 0, "deleted": 0},
        "error": {"updated": 0, "created": 0, "deleted": 0},
    }
    group_task = fetch_group(group_id)
    if group_task is None:
        return "Grupo sin tareas"

    for task in group_task:
        if isinstance(task.result, dict):
            results["success"]["created"] += task.result["success"]["created"]
            results["success"]["updated"] += task.result["success"]["updated"]
            results["success"]["deleted"] += task.result["success"]["deleted"]
            results["error"]["created"] += task.result["error"]["created"]
            results["error"]["updated"] += task.result["error"]["updated"]
            results["error"]["deleted"] += task.result["error"]["deleted"]

    harvest_stage = ControlHarvestStatus(
        group_id=group_id, stage=8, status=3, results=results
    )
    harvest_stage.change_stage_by_step()

    bbl_logger.info(
        _(
            "Cosechamiento de %(set)s [%(source)s]."
            ", Correctos: +%(s_created)s ~%(s_updated)s -%(s_deleted)s"
            ", Errores: +%(e_created)s ~%(e_updated)s -%(e_deleted)s "
        ),
        {
            "set": set_name,
            "source": source_name,
            "s_created": results["success"]["created"],
            "s_updated": results["success"]["updated"],
            "s_deleted": results["success"]["deleted"],
            "e_created": results["error"]["created"],
            "e_updated": results["error"]["updated"],
            "e_deleted": results["error"]["deleted"],
        },
    )
    return results


def harvest_task(data_source, sets, group_id, storage_path, user):
    """
    Entry point to harvest functionality.

    Harvest a DataSource based on the provided configuration.
    This task unloads the work to new sub-tasks.
    """
    # Prepare Files based on Method
    bbl_logger.info(
        _("Inicio de tarea de cosechamiento para fuente: %(source)s"),
        {"source": data_source.name},
    )

    try:

        # Api
        if data_source.config["method"] == "api":
            i = -1
            for a_set in sets:
                i += 1
                harvest_stage = ControlHarvestStatus(
                    data_source=data_source, group_id=f"{group_id},{i}", user=user, stage=1, status=0, a_set=a_set
                )
                harvest_stage.create_stage_first_time()
                harvest_stage.count_total_resources(data_source.config["url"])
                async_task(
                    "harvester.functions.oai.harvest_oai",
                    data_source,
                    data_source.data_mapping,
                    a_set,
                    f"{group_id},{i}",
                    group=f"{group_id},{i}",
                )
        else:
            harvest_stage = ControlHarvestStatus(
                data_source=data_source, group_id=group_id, user=user, stage=1, status=0
            )
            harvest_stage.change_stage_by_step()

        files = []
        if data_source.config["method"] in ["url", "ftp"]:
            try:
                files = download_file_and_upload(
                    data_source.config["url"], data_source, group_id, user
                )
            except Exception:
                bbl_logger.error(
                    _("El archivo no pudo ser descargado: %(path)s"),
                    {"path": data_source.config["url"]},
                )
                raise

        elif data_source.config["method"] == "upload":
            if storage_path is not None:
                files = [storage_path]

        i = -1
        for file in files:
            i += 1
            j = -1
            for a_set in sets:
                j += 1
                args = [
                    data_source,
                    data_source.data_mapping,
                    a_set,
                    file,
                    f"{group_id}",
                ]
                kwargs = {"group": f"{group_id}"}

                harvest_stage.count_total_resources(data_source.config["format"], file)
                # Create task based on format
                if data_source.config["format"] == "csv":
                    async_task(
                        "harvester.functions.csv.harvest_csv_lines", 0, *args, **kwargs
                    )
                elif data_source.config["format"] == "marc_xml":
                    async_task(
                        "harvester.functions.marc.harvest_marc", "xml", *args, **kwargs
                    )

                elif data_source.config["format"] == "marc_plain":
                    async_task(
                        "harvester.functions.marc.harvest_marc",
                        "plain",
                        *args,
                        **kwargs,
                    )
        return True

    except Exception as e:
        harvest_stage.status = 2
        harvest_stage.change_stage_by_step()
        return False


def save_resources(resources_data, data_source, set_instance, group_id):
    """Store resources (create, update) and its relations or equivalences."""
    counters = {
        "success": {"updated": 0, "created": 0, "deleted": 0},
        "error": {"updated": 0, "created": 0, "deleted": 0},
    }

    try:
        # For Indexing
        backend = get_search_backend("default")
        search_index = backend.get_index_for_model(ContentResource)
        index_chunk_size = INDEX_CHUNK_SIZE
        resources_to_index = []

        harvest_stage = ControlHarvestStatus(
            group_id=group_id, stage=6, status=1, data_source=data_source
        )
        harvest_stage.set_calculate_progress(len(resources_data))
        harvest_stage.change_stage_by_step(True)

        resources_dict = {}
        for resource_data in resources_data:
            if "title" not in resource_data or not resource_data["title"]:
                continue
            if "identifier" not in resource_data or not resource_data["identifier"]:
                continue
            try:
                dynamic_identifier = ContentResource.calculate_identifier(
                    resource_data, data_source.dynamicidentifierconfig_set.all()
                )
            except InvalidModelInstance:
                # not Save
                pass
            else:
                if dynamic_identifier not in resources_dict:
                    resource_data["dynamic_identifier_cached"] = dynamic_identifier
                    resource_data["dynamic_identifier_expired"] = False
                    resource_data["dynamic_identifier_expiration"] = (
                        timezone.now() + datetime.timedelta(days=90)
                    )
                    resources_dict[dynamic_identifier] = resource_data

        equivalences_data = {
            field: set() for field in ContentResource.FIELDS_WITH_EQUIVALENCES
        }

        # Atomic transaction needed to block update queries for existing
        # resources (select_for_update).
        # Once we finish the update, resources can be modified again.
        # We depend on existing resources not been added, deleted or modified while
        # we process the data.
        with transaction.atomic():
            # Holder for relations between resources and the set.
            new_set_relations = []

            # Get the ContentResource by descending ID, to ensure we keep only the
            # one with the oldest ID in case of duplicate dynamic_identifier_cached values.
            existing_queryset = (
                ContentResource.objects.select_for_update().filter(
                    dynamic_identifier_cached__in=resources_dict.keys(),
                )
                .order_by("-id")
            )
            existing_resources = {
                resource.dynamic_identifier_cached: resource
                for resource in existing_queryset.iterator()
            }

            # Create instances for new resources.
            new_resources = []
            for dynamic_identifier, resource_data in resources_dict.items():
                if dynamic_identifier in existing_resources:
                    continue
                resource = ContentResource()
                for field, value in resource_data.items():
                    # Add mapped values to list of equivalences
                    if field in equivalences_data:
                        if value:
                            equivalences_data[field].update(value)
                        setattr(resource, f"_mapping_{field}", value)
                        continue
                    setattr(resource, field, value)
                resource.data_source = data_source
                new_resources.append(resource)

            # Save new resources
            try:
                created_resources = ContentResource.objects.bulk_create(new_resources)
                counters["success"]["created"] += len(new_resources)
            except (DataError, IntegrityError):
                counters["error"]["created"] += len(new_resources)

            # Process additional data
            for created_resource in created_resources:
                new_set_relations.append(
                    SetAndResource(
                        set=set_instance,
                        resource=created_resource,
                        harvest_task=group_id,
                    )
                )
                resources_to_index.append(created_resource)
                # Indexing: Bulk indexing of new resources
                if len(resources_to_index) >= index_chunk_size:
                    search_index.add_items(ContentResource, resources_to_index)
                    resources_to_index.clear()

            # Indexing: Bulk indexing of last new resources
            if len(resources_to_index):
                search_index.add_items(ContentResource, resources_to_index)
                resources_to_index.clear()

            # Update Existing Resources
            updated_at = timezone.now()
            for dynamic_identifier, existing_resource in existing_resources.items():
                original_data_source = data_source
                original_set_instance = set_instance

                data_source = DataSource.objects.filter(
                    pk=existing_resource.data_source_id
                ).first()
                set_instance = Set.objects.filter(
                    data_source_id=data_source.pk).first()

                data_source = original_data_source
                set_instance = original_set_instance

                for field, value in resources_dict[dynamic_identifier].items():
                    # Add mapped values to list of equivalences
                    if field in equivalences_data:
                        if value:
                            equivalences_data[field].update(value)
                        setattr(existing_resource, f"_mapping_{field}", value)
                        continue
                    setattr(existing_resource, field, value)
                existing_resource.updated_at = updated_at

            # Save updates
            fields_to_update = [
                model_field
                for model_field, file_field in data_source.data_mapping.items()
                if model_field not in equivalences_data
                and file_field
                and model_field in MAPPABLE_FIELDS
            ] + ["updated_at"]
            try:
                ContentResource.objects.bulk_update(
                    existing_resources.values(), fields_to_update
                )
                counters["success"]["updated"] += len(existing_resources)
            except (DataError, IntegrityError):
                counters["error"]["updated"] += len(existing_resources)

            # Update existing relations for Resources and Sets
            existing_resources_ids = [
                resource.id for resource in existing_resources.values()
            ]
            SetAndResource.objects.filter(
                resource_id__in=existing_resources_ids, set=set_instance
            ).update(harvest_task=group_id)


            resources_to_update = ContentResource.objects.filter(
                id__in=existing_resources_ids
            )
            for resource_update in resources_to_update.iterator(
                chunk_size=index_chunk_size
            ):
                resources_to_index.append(resource_update)
                if len(resources_to_index) >= index_chunk_size:
                    search_index.add_items(ContentResource, resources_to_index)
                    resources_to_index.clear()
            if len(resources_to_index):
                search_index.add_items(ContentResource, resources_to_index)
                resources_to_index.clear()

            SetAndResource.objects.bulk_create(new_set_relations)

            # Create equivalences values
            new_equivalences = []
            for field, values in equivalences_data.items():
                for value in values:
                    if value is None or len(value) > LONG_TEXT:
                        continue
                    new_equivalences.append(
                        ContentResourceEquivalence(original_value=value, field=field)
                    )
            ContentResourceEquivalence.objects.bulk_create(
                new_equivalences, ignore_conflicts=True
            )

            grouped_equivalences = {}
            for field, values in equivalences_data.items():
                grouped_equivalences[field] = {}
                grouped_equivalences[field] = {
                    eq.original_value: eq
                    for eq in ContentResourceEquivalence.objects.filter(
                        field=field, original_value__in=values
                    )
                }

            resources = list(existing_resources.values()) + list(created_resources)

            LanguageEquivalenceRelation.objects.filter(
                contentresource__in=resources
            ).delete()
            SubjectEquivalenceRelation.objects.filter(
                contentresource__in=resources
            ).delete()
            TypeEquivalenceRelation.objects.filter(
                contentresource__in=resources
            ).delete()
            RightsEquivalenceRelation.objects.filter(
                contentresource__in=resources
            ).delete()
            CreatorEquivalenceRelation.objects.filter(
                contentresource__in=resources
            ).delete()

            for field, equivalences in grouped_equivalences.items():
                new_relations = []
                class_name = f"{field.capitalize()}EquivalenceRelation"
                for resource in resources:
                    position = 0
                    # Return list if there is no attribute or if attribute empty
                    for value in getattr(resource, f"_mapping_{field}", None) or []:
                        if value is not None:
                            new_relations.append(
                                globals()[class_name](
                                    contentresource=resource,
                                    contentresourceequivalence=equivalences[value],
                                    position=position,
                                )
                            )
                            position += 1
                globals()[class_name].objects.bulk_create(new_relations)

        return counters

    except Exception as e:
        harvest_stage.status = 2
        harvest_stage.change_stage_by_step()
        return counters


def clean_resources_from_set(instance, group_id):
    """
    Remove ContentResource from a Set if not harvested in the given `group_id`.

    Return the number of Resources removed from the Set.
    """
    set_and_resource_queryset = SetAndResource.objects.filter(set=instance).exclude(
        harvest_task=group_id
    )

    ContentResource.objects.filter(
        id__in=set_and_resource_queryset.values("resource")
    ).update(updated_at=timezone.now(), to_delete=True)

    return set_and_resource_queryset.delete()[0]


def set_positions(positions, record_data):
    """Put the desired element as the first item of a field."""
    for column, first_position in positions.items():
        if column in record_data:
            if record_data[column] is not None and first_position < len(
                record_data[column]
            ):
                record_data[column].insert(0, record_data[column][first_position])
                record_data[column].pop(first_position + 1)
