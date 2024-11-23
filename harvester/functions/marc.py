"""Define functions to harvest MARC sources."""
import logging
import re

import pymarc
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ..models import Set
from .harvester import (
    MAPPABLE_FIELDS,
    clean_resources_from_set,
    log_results_task,
    prepare_file,
    save_resources,
    set_positions,
)

bbl_logger = logging.getLogger("biblored")  # pylint: disable=invalid-name
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def harvest_marc(file_format, data_source, mapping, a_set, storage_path, group_id):
    """Execute a Harvest Task for Marc21 Data Sources."""
    bbl_logger.info(
        _("Inicio de procesamiento para fuente: %(source)s"),
        {"source": data_source.name},
    )

    # Get Set instance
    (spec, name) = a_set
    set_instance = Set.objects.get_or_create(
        spec=spec, data_source=data_source, defaults={"name": name}
    )[0]
    counters = process_marc_file(
        file_format, storage_path, mapping, data_source, set_instance, group_id
    )

    # Delete Relations
    counters["success"]["deleted"] = clean_resources_from_set(set_instance, group_id)
    log_results_task(group_id, set_instance.name, data_source.name)
    return counters


def process_marc_file(
    file_type, file_path, mapping, data_source, set_instance, group_id
):
    """Take a Marc21 File and translate into a ContentResource."""
    # Get the prepared file
    file = prepare_file(file_path)
    counters = {
        "success": {"updated": 0, "created": 0, "deleted": 0},
        "error": {"updated": 0, "created": 0, "deleted": 0},
    }

    records_data = []

    def parse_xml_record(record):
        """Convert a Marc21 XML Record into a database record."""
        record_data = {}
        if record is not None:
            for model_column, mapped_fields in mapping.items():
                if model_column in MAPPABLE_FIELDS:
                    for mapped_field in mapped_fields:
                        if mapped_field:
                            record_data[model_column] = get_marc_record_content(
                                mapped_field, record
                            )
        if record_data:
            set_positions(mapping["positions"], record_data)
            records_data.append(record_data)

        if len(records_data) == settings.TASK_PAGE_LENGTH:
            counter_temp = save_resources(
                records_data, data_source, set_instance, group_id
            )
            counters["success"]["created"] += counter_temp["success"]["created"]
            counters["success"]["updated"] += counter_temp["success"]["updated"]
            counters["success"]["deleted"] += counter_temp["success"]["deleted"]
            counters["error"]["created"] += counter_temp["error"]["created"]
            counters["error"]["updated"] += counter_temp["error"]["updated"]
            counters["error"]["deleted"] += counter_temp["error"]["deleted"]
            records_data.clear()

    if file_type == "plain":
        for record in pymarc.MARCReader(
            file, to_unicode=True, force_utf8=True, utf8_handling="ignore"
        ):
            parse_xml_record(record)
    elif file_type == "xml":
        pymarc.map_xml(parse_xml_record, file)

    file.close()
    if records_data:
        counter_i = save_resources(records_data, data_source, set_instance, group_id)
        counters["success"]["created"] += counter_i["success"]["created"]
        counters["success"]["updated"] += counter_i["success"]["updated"]
        counters["success"]["deleted"] += counter_i["success"]["deleted"]
        counters["error"]["created"] += counter_i["error"]["created"]
        counters["error"]["updated"] += counter_i["error"]["updated"]
        counters["error"]["deleted"] += counter_i["error"]["deleted"]

    return counters


def get_marc_record_content(mapped_field, marc_record):
    """Obtain the content of a Marc21 Record, based on the mapping and a Record."""
    content = []
    for tag in mapped_field.split("|"):
        marc_elements = tag.split("$", 4)
        search_fields = get_search_fields(marc_elements[0], "field")
        search_subfields = get_search_fields(marc_elements[1])
        ind1 = get_search_fields(marc_elements[2])
        ind2 = get_search_fields(marc_elements[3])
        substrings = {}
        found_fields = []
        # Leader and Substrings
        for i, search_field in enumerate(search_fields):
            if "/" in search_field:
                splitted = search_field.split("/")
                search_fields[i] = splitted[0]
                substrings[splitted[0]] = splitted[1]

            if "leader" in search_field.lower():
                sliceargs = [int(s) - 1 for s in re.findall(r"\d+", search_field)] + [
                    None
                ]
                found_fields.append(marc_record.leader[slice(*sliceargs)])
        found_fields += marc_record.get_fields(*search_fields)

        for found_field in found_fields:
            if isinstance(found_field, pymarc.Field):
                if search_subfields:
                    found_subfields = found_field.get_subfields(*search_subfields)
                else:
                    found_subfields = found_field.value()

                if found_field.is_control_field():
                    # control fields has no indicators, but can be slices
                    content += get_marc_subfield(
                        found_subfields, substrings.get(found_field.tag, None)
                    )
                else:
                    # if there are indicators verify
                    if (found_field.indicator1 in ind1 or not ind1) and (
                        found_field.indicator2 in ind2 or not ind2
                    ):
                        content += get_marc_subfield(found_subfields)
            else:
                content += [found_field]
    return content


def get_marc_subfield(found_subfields, substring=None):
    """Obtain the value of a marc21 subfield tag."""
    subfield_content = []
    if not isinstance(found_subfields, (list,)):
        found_subfields = [found_subfields]

    for found_subfield in found_subfields:
        stripped_subfield = found_subfield.strip()
        if stripped_subfield:
            if substring:
                start, stop = substring.split(":", 2)
                subfield_content.append(stripped_subfield[slice(int(start), int(stop))])
            else:
                subfield_content.append(stripped_subfield)
    return subfield_content


def get_search_fields(base_string: object, scope: object = None) -> object:
    """Get the search fields for a MARC mapping notation."""
    # is a range of fields (must be 3 len filled with zeroes)
    if "-" in base_string and scope == "field":
        min_lim, max_lim = base_string.split("-")
        return [str(f).zfill(3) for f in range(int(min_lim), int(max_lim) + 1)]

    # is a range of subfields or indicators
    if "-" in base_string and scope is None:
        min_lim, max_lim = base_string.split("-")
        return [str(f) for f in range(int(min_lim), int(max_lim) + 1)]

    # is a list
    if "," in base_string:
        return base_string.split(",")

    # is a single string
    elif base_string == "":
        return []
    return [str(base_string)]
