"""Script for `runscript schedule_tasks`."""

from django.http import QueryDict

from ..tasks import schedule_index_task, schedule_remove_task


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

    schedule_index_task(**kwargs)
    schedule_remove_task(**kwargs)
