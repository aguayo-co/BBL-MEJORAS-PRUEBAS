"""Define tasks to be executed periodically."""

import datetime

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.models import Schedule

from resources.helpers import unparallel

from .elasticsearch import (
    es_conf,
    get_queryset_for_indexing,
    index_all_resources,
    remove_all_deleted_resources,
)


@unparallel
def index_task(limit):
    """Continuously execute an indexing task."""
    results = index_all_resources(limit)
    result_text = "Indexado periódico: "
    for index_name, cant in results.items():
        result_text += f"[{index_name}] +{cant[0]} ~{cant[1]} "
    return result_text


@unparallel
def schedule_index_task(limit=1000, minutes=2):
    """Schedule index_task to be run once in 1 minute."""
    func = "search_engine.tasks.index_task"
    Schedule.objects.update_or_create(
        name=func,
        next_run=(timezone.now() + datetime.timedelta(minutes=minutes)),
        defaults={
            "name": _("Indexado de Registros en Indice"),
            "kwargs": {"limit": limit},
            "func": func,
            "minutes": minutes,
            "schedule_type": "I",
        },
    )


@unparallel
def first_time_index_task(limit):
    """Continuously execute an indexing task."""
    try:
        index_all_resources(limit, first_time=True)
    finally:
        for model in es_conf.INDEXED_MODELS:
            remain = get_queryset_for_indexing(model, first_time=True).count()
            if remain:
                schedule_first_time_index_task(limit)
                break


def schedule_first_time_index_task(limit=1000, minutes=1):
    """Schedule index_task to be run once in 1 minute."""
    func = "search_engine.tasks.first_time_index_task"
    Schedule.objects.update_or_create(
        name=func,
        defaults={
            "name": _("Indexado Inicial"),
            "kwargs": {"limit": limit},
            "func": func,
            "next_run": (timezone.now() + datetime.timedelta(minutes=minutes)),
        },
    )


@unparallel
def remove_task(limit):
    """Continuously execute a remove indexing task."""
    remove_all_deleted_resources(limit)


def schedule_remove_task(limit=1000, minutes=2):
    """Schedule remove_task to be run once in 1 minute."""
    func = "search_engine.tasks.remove_task"
    Schedule.objects.update_or_create(
        name=func,
        next_run=(timezone.now() + datetime.timedelta(minutes=minutes)),
        defaults={
            "name": _("Eliminación de Registros en Indices"),
            "kwargs": {"limit": limit},
            "func": func,
            "minutes": minutes,
            "schedule_type": "I",
        },
    )
