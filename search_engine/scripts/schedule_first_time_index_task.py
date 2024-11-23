"""Script for `runscript schedule_tasks`."""
from django.http import QueryDict

from ..tasks import schedule_first_time_index_task


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

    schedule_first_time_index_task(**kwargs)
