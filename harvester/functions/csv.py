"""Define functions to harvest CSV files."""
import csv
import io
import logging
from itertools import islice

from django.conf import settings
from django_q.tasks import async_task

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


def harvest_csv_lines(line, data_source, data_mapping, a_set, storage_path, group_id):
    """
    Open a CSV file (txt, tsv, csv) and store its data as a ContentResource.

    This function return true, false or raise an specific exception.
    """
    # CSV Files contains only one set, added for future implementation
    (spec, name) = a_set
    set_instance = Set.objects.get_or_create(
        spec=spec, data_source=data_source, defaults={"name": name}
    )[0]

    file_pointer = prepare_file(storage_path)

    resources_data = []
    # prepare next iteration
    next_line = int(line) + settings.TASK_PAGE_LENGTH
    continue_read = False
    with file_pointer as local_file:
        reader = csv.DictReader(
            io.TextIOWrapper(local_file, encoding="utf-8"),
            delimiter=data_source.config["delimiter"],
            quotechar=data_source.config["quotechar"],
        )

        # read csv with config
        for row in islice(reader, line, next_line):
            continue_read = True
            row_data = {}
            for model_field, file_fields in data_mapping.items():
                if model_field in MAPPABLE_FIELDS:
                    for file_field in file_fields:
                        if file_field in reader.fieldnames:
                            if model_field not in row_data:
                                row_data[model_field] = []
                            row_data[model_field].append(row[file_field].strip())
            if row_data:
                set_positions(data_mapping["positions"], row_data)
                resources_data.append(row_data)
        local_file.close()

    counters = save_resources(resources_data, data_source, set_instance, group_id)
    # Queue next read
    if continue_read:
        async_task(
            "harvester.functions.csv.harvest_csv_lines",
            next_line,
            data_source,
            data_mapping,
            a_set,
            storage_path,
            group_id,
            group=group_id,
        )
    else:
        # Get all Resources with this set set in relation and other group_id
        # Delete the relation and count deleted
        counters["success"]["deleted"] = clean_resources_from_set(
            set_instance, group_id
        )
        log_results_task(group_id, set_instance.name, data_source.name)
    return counters


def get_csv_columns(file, delimiter=",", quotechar='"'):
    """Return the column headers of the provided CSV files."""
    valid_columns = []
    invalid_columns = []

    reader = csv.DictReader(
        io.TextIOWrapper(file, encoding="utf-8"),
        delimiter=delimiter,
        quotechar=quotechar,
    )

    for file_field in reader.fieldnames:
        # Do not allow columns with trailing spaces.
        # They will be used as keys, and it tends to become problematic
        # Sometimes keys are stripped by third party apps, like formtools.wizard.
        if file_field == file_field.strip():
            valid_columns.append(file_field)
        else:
            invalid_columns.append(file_field)

    return valid_columns, invalid_columns
