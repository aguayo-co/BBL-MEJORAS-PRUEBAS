"""Script for `runscript schedule_tasks."""
from django.http import QueryDict

from biblored import settings
from ..helpers import schedule_delete_in_background_task
from ..models import schedule_resource_fields_calculation_task
from ..tasks import (
    schedule_cached_field_update_task,
    schedule_delete_duplicate_resources,
    update_certs,
)


def run(params=None):
    """Ensure latest version of schedules exists."""
    kwargs = {}

    if params:
        minutes = QueryDict(params).get("minutes")
        if minutes is not None:
            kwargs["minutes"] = int(minutes)

        limit = QueryDict(params).get("limit")
        if limit is not None:
            kwargs["limit"] = int(limit)

    schedule_resource_fields_calculation_task(**kwargs)
    schedule_cached_field_update_task(**kwargs)
    schedule_delete_duplicate_resources(**kwargs)
    schedule_delete_in_background_task(**kwargs)
    update_certs()
