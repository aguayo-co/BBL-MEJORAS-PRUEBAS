"""Define functions to harvest OAI sources."""
import logging

from django.conf import settings
from django.db import IntegrityError
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from requests import HTTPError
from sickle import Sickle
from sickle.iterator import OAIResponseIterator
from sickle.models import Record
from sickle.oaiexceptions import BadArgument, BadVerb, NoRecordsMatch

from ..models import Set
from .harvester import (
    MAPPABLE_FIELDS,
    BadSource,
    clean_resources_from_set,
    log_results_task,
    save_resources,
    set_positions,
)

bbl_logger = logging.getLogger("biblored")  # pylint: disable=invalid-name
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def harvest_oai(
    data_source, mapping, a_set, group_id, attempt=1, sickle_responses=None
):
    """Execute a Harvest Task for OAI-PMH data sources with Dublin Core Format."""
    counters = {
        "success": {"updated": 0, "created": 0, "deleted": 0},
        "error": {"updated": 0, "created": 0, "deleted": 0},
    }
    (spec, name) = a_set
    try:
        set_instance = Set.objects.get_or_create(
            spec=spec, data_source=data_source, defaults={"name": name, "visible": True}
        )[0]
    except IntegrityError:
        set_instance = Set.objects.get(spec=spec, data_source=data_source)

    records_data = []
    sickle_instance = Sickle(
        data_source.config["url"],
        iterator=OAIResponseIterator,
        verify=False,
        headers={"user-agent": "PostmanRuntime/7.25.0"},
    )
    if sickle_responses is None:
        # First Response
        try:
            sickle_responses = sickle_instance.ListRecords(
                set=set_instance.spec, metadataPrefix="oai_dc", ignore_deleted=True
            )
        except NoRecordsMatch:
            bbl_logger.error(
                format_lazy(
                    _("Set vacío: {} - Cosechamiento de fuente: {}"),
                    set_instance.name,
                    data_source.name,
                )
            )
            counters["success"]["deleted"] = clean_resources_from_set(
                set_instance, group_id
            )
            log_results_task(group_id, set_instance.name, data_source.name)

            return counters

    try:
        current_page = sickle_responses.next()
    except StopIteration:
        # Delete and count deleted
        counters["success"]["deleted"] = clean_resources_from_set(
            set_instance, group_id
        )
        log_results_task(group_id, set_instance.name, data_source.name)

        return counters
    except Exception:
        bbl_logger.error(
            format_lazy(
                _(
                    "Error de cosechamiento, detalles en tareas fallidas, Set {} - Fuente {}"
                ),
                set_instance.name,
                data_source.name,
            )
        )
        if attempt < settings.FAILED_TASK_ATTEMPTS:
            async_task(
                "harvester.functions.oai.harvest_oai",
                data_source,
                data_source.data_mapping,
                a_set,
                group_id,
                attempt + 1,
                group=group_id,
            )
            return True

        bbl_logger.error(
            format_lazy(
                _("{} intentos fallidos para: Set {} - Fuente {}"),
                settings.FAILED_TASK_ATTEMPTS,
                set_instance.name,
                data_source.name,
            )
        )
        raise
    else:
        for element in current_page.xml.iter(tag="{*}record"):
            record = Record(element, strip_ns=True)
            if hasattr(record, "metadata"):
                record_data = {}
                for model_column, record_fields in mapping.items():
                    if model_column in MAPPABLE_FIELDS:
                        for record_field in record_fields:
                            if model_column not in record_data:
                                record_data[model_column] = []
                            record_data[model_column] = record.metadata.get(
                                record_field, None
                            )
                # Set Positions
                set_positions(mapping["positions"], record_data)
                records_data.append(record_data)

    # Create or update
    counters = save_resources(records_data, data_source, set_instance, group_id)

    # Create new Task
    async_task(
        "harvester.functions.oai.harvest_oai",
        data_source,
        data_source.data_mapping,
        a_set,
        group_id,
        1,
        sickle_responses,
        group=group_id,
    )

    return counters


def get_sets_oai(data_source):
    """Return the sets from an OAI api."""
    sickle = Sickle(
        data_source.config["url"],
        verify=False,
        headers={"user-agent": "PostmanRuntime/7.25.0"},
    )

    try:
        raw_sets = sickle.ListSets()
    except (BadArgument, BadVerb, HTTPError):
        raise BadSource

    sets = []
    for a_set in raw_sets:
        if hasattr(a_set, "setSpec"):
            sets.append((a_set.setSpec, a_set.setName))
        else:
            sets.append((a_set.setName, a_set.setName))
    return sets
