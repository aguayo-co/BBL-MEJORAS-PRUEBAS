"""Elastic search frontend API helpers."""

import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    OuterRef,
    Subquery,
    F,
    Q,
    BooleanField,
    DateTimeField,
    ExpressionWrapper,
    Exists,
)
from elasticsearch.helpers import bulk

from harvester.models import SetAndResource
from .. import config as es_conf
from ..models import IndexedResource

ELASTICSEARCH_CLIENT = es_conf.ELASTICSEARCH_CLIENT

CHUNK_SIZE = 400

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

#########################################
# Backend API helper functions          #
#########################################


# Bulk indexing


def bulk_create_or_update(queryset):
    """Realiza el indexado masivo de un queryset."""
    return bulk(
        ELASTICSEARCH_CLIENT,
        yield_create_or_update_document_mapping(queryset),
        stats_only=True,
        raise_on_error=False,
    )


def yield_create_or_update_document_mapping(queryset):
    """Recorre un queryset y hace un yield del mapeo de campos de cada instancia."""
    model = queryset.model
    index_name = es_conf.get_indice_name(model)

    for instance in queryset.iterator(chunk_size=CHUNK_SIZE):
        yield get_create_or_update_yield_mapping(
            instance=instance, index_name=index_name
        )


def get_create_or_update_yield_mapping(instance, index_name):
    """
    Retorna el dict necesario para el yield del indexado masivo.

    Retorna un dict que contiene el mapeo de campos de una instancia de un queryset
    usado para el indexado masivo, toma la estructura establecida en el dict
    `es_conf.BULK_INDEX_FIELDS_MAPPING` según el índice seleccionado
    """
    # Index document attributes
    yield_map = {
        "_index": index_name,
        "_type": "_doc",
        "_source": {},
        "_id": f"{instance._meta.model_name}-{getattr(instance, 'pk')}",
    }

    for field_name, field_settings in es_conf.BULK_INDEX_FIELDS_MAPPING[
        index_name
    ].items():
        add_field_to_yield_map(instance, field_name, field_settings, yield_map)

    return yield_map


def get_instance_field_name(instance, index_field_name, index_field_settings):
    """Obtiene el nombre del atributo de una instancia a partir del campo del índice"""
    instance_field_name = None

    if hasattr(instance, index_field_name):
        instance_field_name = index_field_name
    elif (
        "alt_name" in index_field_settings
        and instance._meta.model_name in index_field_settings["alt_name"]
    ):
        instance_field_name = index_field_settings["alt_name"][
            instance._meta.model_name
        ]

    return instance_field_name


def add_field_to_yield_map(instance, field_name, field_settings, yield_map):
    """Extract field data from instance and add it to the yield_map."""

    if field_settings["type"] == "primary_key":
        value = int(getattr(instance, field_name))
        if value is not None:
            yield_map["_source"][field_name] = value
        return

    if field_settings["type"] == "model_name":
        subtype_model = (
            instance.get_subtype() if hasattr(instance, "get_subtype") else None
        )
        yield_map["_source"][field_name] = subtype_model or instance._meta.model_name
        return

    instance_field_name = get_instance_field_name(instance, field_name, field_settings)

    if field_settings["type"] == "boolean":
        field_values = getattr(instance, instance_field_name)
        if not isinstance(field_values, list):
            field_values = [field_values]
        field_values = [bool(value) for value in field_values]
        yield_map["_source"][field_name] = field_values
        return

    if field_settings["type"] == "integer":
        value = int(getattr(instance, instance_field_name))
        if value is not None:
            yield_map["_source"][field_name] = value
        return

    if field_settings["type"] == "text":
        yield_map["_source"][field_name] = limit_field_size(
            getattr(instance, instance_field_name)
        )
        return

    if field_settings["type"] == "processed_text":
        yield_map["_source"][field_name] = limit_field_size(
            getattr(instance.processed_data, instance_field_name)
        )
        return

    if field_settings["type"] == "content_resource_equivalence":
        yield_map["_source"][field_name] = list(
            getattr(instance, instance_field_name).values_list(
                "original_value", flat=True
            )
        )
        return

    if field_settings["type"] == "exposition_equivalence":
        yield_map["_source"][field_name] = list(
            getattr(instance, instance_field_name).name
        )
        return

    if field_settings["type"] == "timestamp":
        yield_map["_source"][field_name] = getattr(
            instance, instance_field_name
        ).timestamp()
        return

    if field_settings["type"] == "processed_value":
        value = getattr(instance.processed_data, field_name)
        if value is not None:
            yield_map["_source"][field_name] = value
        return

    if field_settings["type"] == "join":
        for sub_field_name, sub_field_settings in field_settings[
            "sub_fields"  # pylint: disable=bad-continuation
        ].items():
            if (
                sub_field_settings["type"] in ["text", "integer", "boolean"]
                and instance_field_name
            ):
                value = getattr(getattr(instance, instance_field_name), sub_field_name)
            else:
                value = None
            yield_map["_source"][field_name + "_" + sub_field_name] = value

    if field_settings["type"] == "many_to_many":
        value = getattr(instance, instance_field_name)
        yield_map["_source"][field_name] = list(
            value.all().values_list("pk", flat=True)
        )


def limit_field_size(data):
    """
    Limit size of indexed field to avoid errors.

    Fields with excessive size generate errors on Elastic. Cut the size
    of each field to avoid that.
    """
    limit = 5000

    if isinstance(data, str):
        return data.strip()[:limit]

    if isinstance(data, list):
        total_size = 0
        limited_data = []
        for element in data:
            if element is not None and isinstance(element, str):
                element = element.strip()
                total_size += len(element)
                if total_size > limit:
                    excess = total_size - limit
                    limited_data.append(element[:-excess])
                    break
                limited_data.append(element)
        return limited_data
    return data


def get_queryset_for_indexing(model, limit=None, first_time=False):
    """Obtiene los todos recursos de un modelo que deben ser indexados."""
    queryset = (
        get_base_model_queryset(model)
        .annotate(
            indexed_at=Subquery(
                get_subquery_indexed_resource(model).values("indexed_at"),
                output_field=DateTimeField(),
            ),
            need_to_index=Subquery(
                get_subquery_indexed_resource(model).values("need_to_index"),
                output_field=BooleanField(),
            ),
        )
        .order_by("indexed_at")
    )

    if (
        model._meta.app_label == "harvester"
        and model._meta.model_name == "contentresource"
    ):
        queryset = queryset.order_by(
            F("indexed_at").asc(nulls_last=False), F("updated_at").asc(nulls_last=True)
        )
    else:
        queryset = queryset.order_by(F("indexed_at").asc(nulls_last=False))

    if first_time:
        extra_annotate = get_extra_queryset_annotate_for_first_time_indexing(model)
        filters = get_model_queryset_for_first_time_indexing_filters(model)
    else:
        extra_annotate = get_extra_queryset_annotate_for_indexing(model)
        filters = get_model_queryset_for_indexing_filters(model)

    if extra_annotate:
        queryset = queryset.annotate(**extra_annotate)

    if filters:
        queryset = queryset.filter(filters)

    # TODO Evitar este distinct en first_time=True.
    return queryset.distinct()[:limit]


def get_extra_queryset_annotate_for_indexing(model):
    """Obtiene condiciones extras para el annotate si existen."""
    return es_conf.MODEL_PARAMS[model._meta.model_name].get(
        "extra_queryset_annotate_for_indexing"
    )


def get_extra_queryset_annotate_for_first_time_indexing(model):
    """Obtiene condiciones extras para el annotate si existen."""
    return es_conf.MODEL_PARAMS[model._meta.model_name].get(
        "extra_queryset_annotate_for_first_time_indexing"
    )


def get_base_model_queryset(model):
    """Obtiene queryset base del modelo y sus relaciones necesarias para el indexado."""
    return es_conf.MODEL_PARAMS[model._meta.model_name].get(
        "base_model_queryset", model.objects
    )


def get_model_queryset_for_indexing_filters(model):
    """Obtiene los filtros aplicados al queryset para indexar de un modelo."""
    return es_conf.MODEL_PARAMS[model._meta.model_name].get(
        "queryset_for_indexing_filters"
    )


def get_model_queryset_for_first_time_indexing_filters(model):
    """Obtiene los filtros aplicados al queryset para indexar de un modelo."""
    return es_conf.MODEL_PARAMS[model._meta.model_name].get(
        "queryset_for_first_time_indexing_filters"
    )


def get_subquery_indexed_resource(model):
    """Obtiene subquery para relacionar recursos con modelo de control de indexado."""
    return IndexedResource.objects.filter(
        object_id=OuterRef("id"),
        content_type=ContentType.objects.filter(
            app_label=model._meta.app_label, model=model._meta.model_name
        )[:1],
    )


def create_or_update_indexed_at_register(queryset, date):
    """Crea o actualiza registros en el modelo IndexedResource."""
    total_created = 0
    total_updated = 0

    to_create = []
    to_update = []

    def update(to_update):
        content_type_to_update = ContentType.objects.filter(
            app_label=queryset.model._meta.app_label,
            model=queryset.model._meta.model_name,
        )[:1]
        return IndexedResource.objects.filter(
            object_id__in=to_update, content_type=content_type_to_update
        ).update(indexed_at=date, need_to_index=False)

    def create(to_create):
        return len(IndexedResource.objects.bulk_create(to_create))

    for instance in queryset.iterator(chunk_size=CHUNK_SIZE):
        if instance.indexed_at:
            to_update.append(instance.pk)
            if len(to_update) > CHUNK_SIZE:
                total_updated += update(to_update)
                to_update = []
            continue

        to_create.append(IndexedResource(content_object=instance, indexed_at=date))
        if len(to_create) > CHUNK_SIZE:
            total_created += create(to_create)
            to_create = []

    if to_update:
        total_updated += update(to_update)

    if to_create:
        total_created += create(to_create)

    logger.info("Se crearon %s registros de indexado", total_created)
    logger.info("Se actualizaron %s registros de indexado", total_updated)
    return total_created, total_updated


# Bulk deleting


def bulk_delete(index_model, queryset):
    """Realiza el borrado masivo de una lista de documentos."""
    return bulk(
        ELASTICSEARCH_CLIENT,
        yield_delete_document_mapping(index_model, queryset),
        stats_only=True,
        raise_on_error=False,
    )


def yield_delete_document_mapping(index_model, queryset):
    """Hace un yield del mapeo de campos para cada documento del list."""
    index_name = es_conf.get_indice_name(index_model)
    for instance in queryset.iterator(chunk_size=CHUNK_SIZE):
        yield {
            "_op_type": "delete",
            "_index": index_name,
            "_type": "_doc",
            "_id": f"{index_name}-{getattr(instance, 'object_id')}",
        }


def get_queryset_for_deleting(model, limit=None):
    """Obtiene los todos recursos de un modelo que deben ser eliminados."""
    return IndexedResource.objects.alias(
        visible_resource=ExpressionWrapper(
            Exists(
                SetAndResource.objects.filter(
                    Q(resource__visible=True) & Q(set__visible=True),
                    resource=OuterRef("object_id"),
                )
            ),
            output_field=BooleanField(),
        ),
    ).filter(
        content_type=ContentType.objects.get(
            app_label=model._meta.app_label, model=model._meta.model_name
        ),
        visible_resource=False,
    )[
        :limit
    ]


# Force reindex


def mark_all_resources_for_reindex():
    """Marca como necesita indexarse a recursos del queryset seleccionado."""
    for model in es_conf.INDEXED_MODELS:
        queryset = model.objects.all()
        mark_resources_for_reindex(queryset)


def mark_resources_for_reindex(queryset):
    """Marca como necesita indexarse a recursos del queryset seleccionado."""
    model = queryset.model
    updated_count = IndexedResource.objects.filter(
        object_id__in=queryset,
        content_type=ContentType.objects.filter(
            app_label=model._meta.app_label, model=model._meta.model_name
        )[:1],
    ).update(need_to_index=True)
    if updated_count:
        logger.info("Se han marcado para reindexar %s recursos", updated_count)


def mark_resource_for_reindex(resource):
    """Marca como necesita indexarse a recursos del queryset seleccionado."""
    model = resource._meta.model
    updated_count = IndexedResource.objects.filter(
        object_id=resource.pk,
        content_type=ContentType.objects.filter(
            app_label=model._meta.app_label, model=model._meta.model_name
        )[:1],
    ).update(need_to_index=True)
    if updated_count:
        logger.info("Se han marcado para reindexar %s recursos", updated_count)
