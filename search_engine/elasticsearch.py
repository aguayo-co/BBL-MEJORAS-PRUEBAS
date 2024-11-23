"""Elastic Search Functions."""

import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Subquery
from django.utils import timezone
from elasticsearch import RequestError

from . import config as es_conf
from .functions.es_backend_helpers import (
    bulk_create_or_update,
    bulk_delete,
    create_or_update_indexed_at_register,
    get_queryset_for_deleting,
    get_queryset_for_indexing,
)
from .functions.es_frontend_helpers import (
    get_data_for_search_with_requests,
    get_didyoumean_args_for_search_with_elasticsearchpy,
    get_didyoumean_formatted_response,
    get_model_suggestions,
    get_search_formatted_response,
    search_with_elasticsearchpy,
    search_with_requests,
)
from .models import IndexedResource

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

ELASTICSEARCH_CLIENT = es_conf.ELASTICSEARCH_CLIENT

CHUNK_SIZE = 400


#########################################
# Frontend API functions                #
#########################################


def search(model, **kwargs):
    """Realiza una búsqueda en el índice del modelo seleccionado."""
    data = get_data_for_search_with_requests(model, **kwargs)
    index_name = es_conf.get_indice_name(model)
    elasticsearch_response = search_with_requests(indexes_list=[index_name], data=data)
    return get_search_formatted_response(model, elasticsearch_response)


def get_suggestions(search_text, **kwargs):
    """Obtiene sugerencias de los índices existentes."""
    return {
        model._meta.model_name: get_model_suggestions(model, search_text, **kwargs)
        for model in es_conf.SEARCH_MODELS
    }


def get_didyoumean(model, search_text):
    """Obtiene `did_you_mean` del índice seleccionado."""
    (
        elasticsearchpy_args,
        is_term_suggest,
    ) = get_didyoumean_args_for_search_with_elasticsearchpy(model, search_text)
    index_name = es_conf.get_indice_name(model)
    elasticsearch_response = search_with_elasticsearchpy(
        indexes_list=[index_name],
        body=elasticsearchpy_args["body"],
        params=elasticsearchpy_args["params"],
    )
    return get_didyoumean_formatted_response(
        model, elasticsearch_response, is_term_suggest
    )


#########################################
# Backend API functions                 #
#########################################


def create_all_indexes():
    """Crea todos los índices en el servidor de elasticsearch."""
    for model in es_conf.INDICES_MODELS:
        if not model._meta.model_name == "contentresource":
            create_index(model)


def create_index(model):
    """Crea un índice en el servidor de elasticsearch."""
    index_name = es_conf.get_indice_name(model)
    try:
        elasticsearch_response = ELASTICSEARCH_CLIENT.indices.create(
            index=index_name,
            body=es_conf.INDICES_CONFIG[index_name],
            include_type_name=True,
        )
    except RequestError:
        elasticsearch_response = ELASTICSEARCH_CLIENT.indices.create(
            index=index_name,
            body=es_conf.INDICES_CONFIG[index_name],
        )

    if elasticsearch_response["acknowledged"]:
        logger.info(
            "Se ha creado satisfactoriamente el indice %s",
            elasticsearch_response["index"],
        )


def delete_all_indexes():
    """Crea todos los índices en el servidor de elasticsearch."""
    for model in es_conf.INDICES_MODELS:
        delete_index(model)


def delete_index(model):
    """Elimina un índice en el servidor de elasticsearch."""
    index_name = es_conf.get_indice_name(model)
    # pylint: disable=unexpected-keyword-arg
    elasticsearch_response = ELASTICSEARCH_CLIENT.indices.delete(
        index=index_name, ignore_unavailable=True
    )
    # pylint: enable=unexpected-keyword-arg
    if elasticsearch_response["acknowledged"]:
        logger.info("Se ha eliminado satisfactoriamente el indice %s", index_name)


def recreate_all_indexes():
    """Elimina y crea los índices y limpia la tabla de registros de indexado."""
    delete_all_indexes()
    create_all_indexes()
    queryset = IndexedResource.objects.all()
    queryset._raw_delete(queryset.db)  # pylint: disable=protected-access


def recreate_index(model):
    """Elimina y crea el índice de un modelo específico.

    Limpia la tabla de registros indexados de ese modelo.
    """
    delete_index(model)
    create_index(model)
    content_type = ContentType.objects.get(
        app_label=model._meta.app_label, model=model._meta.model_name
    )
    queryset = IndexedResource.objects.filter(content_type=content_type)
    queryset._raw_delete(queryset.db)  # pylint: disable=protected-access


# Indexing


def clear_all_indexes():
    """Elimina todos los documentos de los índices."""
    empty_all_indexes()
    queryset = IndexedResource.objects.all()
    queryset._raw_delete(queryset.db)  # pylint: disable=protected-access


def index_all_resources(limit=None, first_time=False):
    """Indexa los recursos que deben ser indexados en todos los models indexados."""
    results = {}
    for model in es_conf.INDEXED_MODELS:
        if not model._meta.model_name == "contentresource":
            results[es_conf.get_indice_name(model)] = index_resources(
                model=model, limit=limit, first_time=first_time
            )
    return results


def index_resources(model, limit=None, first_time=False):
    """
    Indexa recursos de un modelo.

    El modelo seleccionado debe estar en la lista es_conf.INDEXED_MODELS.
    """
    queryset = get_queryset_for_indexing(model, limit, first_time=first_time)
    return index_resources_queryset(queryset, limit)


def index_resources_queryset(queryset, limit=None):
    """
    Indexa y actualiza registros en elastic.

    Indexa las instancias de un queryset y crea o actualiza sus respectivos registros
    en la tabla del modelo IndexedResource
    """
    now = timezone.now()
    if limit:
        queryset = queryset[:limit]
    elasticsearch_bulk_response = bulk_create_or_update(queryset)
    logger.info(
        "Se indexaron %s documentos con éxito en el indice %s",
        elasticsearch_bulk_response[0],
        es_conf.get_indice_name(queryset.model),
    )

    if elasticsearch_bulk_response[1]:
        logger.error(
            "Error indexando %s documentos en el indice %s",
            elasticsearch_bulk_response[1],
            es_conf.get_indice_name(queryset.model),
        )

    return create_or_update_indexed_at_register(queryset, now)


# Deleting
def remove_all_deleted_resources(limit=None):
    """Actualiza los índices eliminando los recursos que ya no existan en la bd."""
    for index_model in es_conf.INDEXED_MODELS:
        if not index_model._meta.model_name == "contentresource":
            remove_deleted_resources(index_model, limit)


def remove_deleted_resources(index_model, limit=None):
    """Elimina los recursos que ya no existan en la tabla del modelo."""
    queryset = get_queryset_for_deleting(index_model, limit)
    remove_deleted_resources_queryset(index_model, queryset, limit)


def remove_deleted_resources_queryset(index_model, queryset, limit=None):
    """
    Elimina registros en elasticsearch.

    Elmina las instancias de un queryset en su índice de elasticsearch y
    elimina sus respectivos registros en la tabla del modelo IndexedResource
    """
    if limit:
        queryset = queryset[:limit]
    elasticsearch_bulk_response = bulk_delete(index_model, queryset)
    logger.info(
        "Se eliminaron %s documentos con éxito en el indice %s",
        elasticsearch_bulk_response[0],
        es_conf.get_indice_name(index_model),
    )

    if elasticsearch_bulk_response[1]:
        logger.error(
            "Error eliminando %s documentos en el indice %s",
            elasticsearch_bulk_response[1],
            es_conf.get_indice_name(index_model),
        )

    deleted_count = IndexedResource.objects.filter(
        pk__in=Subquery(queryset.values("pk"))
    ).delete()
    logger.info("Se eliminaron %s registros de indexado", deleted_count[0])


def empty_all_indexes():
    """Borrar todos los documentos de todos los índices."""
    for model in es_conf.INDICES_MODELS:
        empty_index(model)


def empty_index(model):
    """Borrar todos los documentos de un índice."""
    index_name = es_conf.get_indice_name(model)
    query = {"query": {"match_all": {}}}
    elasticsearch_response = ELASTICSEARCH_CLIENT.delete_by_query(
        index=index_name, body=query
    )
    logger.info(
        "Se eliminaron %s documentos de %s documentos encontrados en el índice %s",
        elasticsearch_response["deleted"],
        elasticsearch_response["total"],
        index_name,
    )
