"""Variables de configuración para Elasticsearch."""

from django.conf import settings
from django.db.models import (
    BooleanField,
    DateTimeField,
    Exists,
    F,
    Max,
    OuterRef,
    Q,
    Subquery,
    Value,
)
from elasticsearch import Elasticsearch

from expositions.models.pages import Exposition
from harvester.models.models import Collection, ContentResource, Set

ELASTICSEARCH_CLIENT = Elasticsearch([settings.SEARCHBOX_SSL_URL_API])


#########################################
# Helper functions                      #
#########################################


def get_indice_name(model):
    """Obtiene el nombre del índice según el modelo seleccionado."""
    # Usa el indice Collection para Sets
    if model is Set:
        return Collection._meta.model_name

    if model is ContentResource:
        return "wagtail__harvester_contentresource"

    # Usa el indice Collection para Colecciones Colaborativas
    for model_class in INDEXED_MODELS:
        if issubclass(model, model_class):
            return model_class._meta.model_name

    return model._meta.model_name


#########################################
# Helper constants                      #
#########################################

# Indexed models
INDEXED_MODELS = [ContentResource, Collection, Exposition, Set]
INDICES_MODELS = [ContentResource, Collection, Exposition]

# Searchables models
SEARCH_MODELS = [ContentResource, Collection, Exposition]

# Analizers, filters y normalizers used for index settings and mappings
INDICES_SETTINGS_ANALIZERS = {
    "suggestions": {
        "type": "custom",
        "tokenizer": "lowercase",
        "filter": ["asciifolding", "suggestions_ngram"],
    },
    "lowercase-asciifolding": {
        "type": "custom",
        "tokenizer": "standard",
        "filter": ["lowercase", "asciifolding"],
    },
}
INDICES_SETTINGS_FILTERS = {
    "lowercase": {"type": "lowercase"},
    "suggestions_ngram": {"type": "ngram", "min_gram": 3, "max_gram": 3},
}
INDICES_SETTINGS_NORMALIZERS = {
    "lowercase": {"type": "custom", "filter": ["lowercase", "asciifolding"]}
}

#########################################
# Backend config constants              #
#########################################


# Indexed models settings and mappings for index creation
INDICES_CONFIG = {
    "_default": {
        "mappings": {
            "properties": {
                "pk": {"type": "integer"},
                "didyoumean": {"type": "text"},
                "description": {
                    "type": "text",
                    "analyzer": "lowercase-asciifolding",
                    "fields": {"keyword": {"type": "keyword"}},
                    "copy_to": ["didyoumean"],
                },
                "title": {
                    "type": "text",
                    "analyzer": "lowercase-asciifolding",
                    "fields": {
                        "keyword": {"type": "keyword"},
                        "suggestions": {
                            "type": "text",
                            "analyzer": "suggestions",
                            "search_analyzer": "standard",
                        },
                    },
                    "copy_to": ["didyoumean"],
                },
            }
        },
        "settings": {
            "index": {
                "analysis": {
                    "analyzer": INDICES_SETTINGS_ANALIZERS,
                    "filter": INDICES_SETTINGS_FILTERS,
                    "normalizer": INDICES_SETTINGS_NORMALIZERS,
                }
            }
        },
    }
}
INDICES_CONFIG["wagtail__harvester_contentresource"] = {
    "mappings": {
        "properties": {
            **INDICES_CONFIG["_default"]["mappings"]["properties"],
            "date_field_filter": {"type": "date", "format": "strict_date"},
            "collection_set": {"type": "long"},
            "sets": {"type": "long"},
            "created_at": {"type": "date", "format": "epoch_millis"},
            "creator_field": {
                "type": "text",
                "analyzer": "lowercase-asciifolding",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": ["didyoumean"],
            },
            "data_source_id_filter": {"type": "integer"},
            "data_source_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "data_source_online_resources": {"type": "boolean"},
            "data_source_relevance_filter": {"type": "integer"},
            "calculated_group_hash": {"type": "keyword"},
            "has_visible_set": {"type": "boolean"},
            "identifier": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "language_field_filter": {"type": "keyword"},
            "publisher": {"type": "text"},
            "rights_field_filter": {"type": "keyword"},
            "subject_field": {
                "type": "text",
                "analyzer": "lowercase-asciifolding",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": ["didyoumean"],
            },
            "type_field_filter": {"type": "keyword"},
            "updated_at": {"type": "date", "format": "epoch_millis"},
            "visible": {"type": "boolean"},
        }
    },
    "settings": {**INDICES_CONFIG["_default"]["settings"]},
}
INDICES_CONFIG[get_indice_name(Collection)] = {
    "mappings": {
        "properties": {
            **INDICES_CONFIG["_default"]["mappings"]["properties"],
            "collection_type": {"type": "keyword"},
            "created_at": {"type": "date", "format": "epoch_millis"},
            "home_site": {"type": "boolean"},
            "home_internal": {"type": "boolean"},
            "model_name": {"type": "keyword"},
            "owner_id": {"type": "integer"},
            "data_source_id": {"type": "integer"},
            "data_source_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "data_source_online_resources": {"type": "boolean"},
            "data_source_relevance": {"type": "integer"},
            "public": {"type": "boolean"},
            "updated_at": {"type": "date", "format": "epoch_millis"},
            "visible": {"type": "boolean"},
        }
    },
    "settings": {**INDICES_CONFIG["_default"]["settings"]},
}
INDICES_CONFIG[get_indice_name(Exposition)] = {
    "mappings": {
        "properties": {
            **INDICES_CONFIG["_default"]["mappings"]["properties"],
            "expired": {"type": "boolean"},
            "live": {"type": "boolean"},
            "subject": {
                "type": "text",
                "analyzer": "lowercase-asciifolding",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": ["didyoumean"],
            },
        }
    },
    "settings": {**INDICES_CONFIG["_default"]["settings"]},
}

# Indexed models Model/Index mapping for bulk indexing
BULK_INDEX_FIELDS_MAPPING = {
    "_default": {
        "pk": {"type": "primary_key"},
        "description": {"type": "text"},
        "title": {"type": "text"},
    }
}
BULK_INDEX_FIELDS_MAPPING["wagtail__harvester_contentresource"] = {
    **BULK_INDEX_FIELDS_MAPPING["_default"],
    "date_field_filter": {"type": "processed_value"},
    "collection_set": {"type": "many_to_many"},
    "sets": {"type": "many_to_many"},
    "created_at": {"type": "timestamp"},
    "creator_field": {"type": "processed_text"},
    "data_source": {
        "type": "join",
        "sub_fields": {
            "id": {"type": "integer"},
            "name": {"type": "text"},
            "relevance": {"type": "integer"},
            "online_resources": {"type": "boolean"},
        },
    },
    "calculated_group_hash": {
        "type": "keyword",
        "alt_name": {ContentResource._meta.model_name: "calculated_group_hash"},
    },
    "has_visible_set": {"type": "boolean"},
    "language": {"type": "content_resource_equivalence"},
    "publisher": {"type": "processed_text"},
    "rights_field_filter": {"type": "content_resource_equivalence"},
    "subject_field": {"type": "content_resource_equivalence"},
    "type_field_filter": {"type": "content_resource_equivalence"},
    "updated_at": {"type": "timestamp"},
    "visible": {"type": "boolean"},
}
BULK_INDEX_FIELDS_MAPPING[get_indice_name(Collection)] = {
    **BULK_INDEX_FIELDS_MAPPING["_default"],
    "collection_type": {"type": "model_name"},
    "created_at": {"type": "timestamp"},
    "home_site": {"type": "boolean"},
    "home_internal": {"type": "boolean"},
    "owner": {
        "type": "join",
        "sub_fields": {"id": {"type": "integer"}},
    },
    "data_source": {
        "type": "join",
        "sub_fields": {
            "id": {"type": "integer"},
            "name": {"type": "text"},
            "relevance": {"type": "integer"},
            "online_resources": {"type": "boolean"},
        },
    },
    "public": {"type": "boolean", "alt_name": {Set._meta.model_name: "visible"}},
    "title": {"type": "text", "alt_name": {"set": "name"}},
    "updated_at": {"type": "timestamp"},
    "visible": {"type": "boolean"},
}
BULK_INDEX_FIELDS_MAPPING[get_indice_name(Exposition)] = {
    **BULK_INDEX_FIELDS_MAPPING["_default"],
    "expired": {"type": "boolean"},
    "live": {"type": "boolean"},
    "subject": {"type": "exposition_equivalence"},
}

######################################
# Model config constants             #
######################################


# Indexed models params used in API functions
MODEL_PARAMS = {
    "_default": {
        "_source_fields": {
            "for_search": "pk",
            "for_suggestions": "title",
            "for_didyoumean": False,
        },
        "didyoumean": {
            "suggest_block_name": "didyoumean_suggestions",
            "phrase_suggest_params": {
                "field": "title",
                "size": 20,
                "highlight": {"pre_tag": "<em>", "post_tag": "</em>"},
                "direct_generator": [
                    {
                        "field": "title",
                        "suggest_mode": "popular",
                        "prefix_length": 0,
                        "min_word_length": 2,
                        "max_inspections": 10,
                    }
                ],
            },
            "term_suggest_params": {"field": "didyoumean", "suggest_mode": "popular"},
        },
        "extra_queryset_annotate_for_first_time_indexing": None,
        "extra_queryset_annotate_for_indexing": None,
        "group_by": {"aggs_name": None, "field": None, "sort": None},
        "queryset_for_first_time_indexing_filters": None,
        "queryset_for_indexing_filters": (Q(indexed_at=None) | Q(need_to_index=True)),
        "range_fields": {"publish_year": None},
        "search_fields": {"for_search": ["*"], "for_suggestions": ["*"]},
        "search_system_filters": None,
        "search_system_sortby": {"_score": {}},
        "sort_rules": {
            "az": {
                "_script": {
                    "type": "string",
                    "script": {"source": "params._source.title[0].toLowerCase()"},
                    "order": "asc",
                }
            },
            "za": {
                "_script": {
                    "type": "string",
                    "script": {"source": "params._source.title[0].toLowerCase()"},
                    "order": "desc",
                }
            },
            "recent": {"updated_at": "desc"},
            "-recent": {"updated_at": "asc"},
        },
    }
}
MODEL_PARAMS[ContentResource._meta.model_name] = {
    **MODEL_PARAMS["_default"],
    "base_model_queryset": ContentResource.objects.select_related("data_source"),
    "extra_queryset_annotate_for_first_time_indexing": {
        "has_visible_set": Value(True, output_field=BooleanField())
    },
    "extra_queryset_annotate_for_indexing": {
        "has_visible_set": Exists(
            Set.objects.filter(contentresource=OuterRef("id")).visible()
        ),
        # "calculated_group_hash": F("calculated_group_hash"),
        # https://docs.djangoproject.com/en/2.2/ref/models/expressions/#using-aggregates-within-a-subquery-expression
        "sets__updated_at__max": Subquery(
            Set.objects.filter(contentresource=OuterRef("id"))
            .visible()
            .order_by()
            .values("visible")
            .annotate(updated_at__max=Max("updated_at"))
            .values("updated_at__max"),
            output_field=DateTimeField(),
        ),
    },
    "group_by": {
        "aggs_name": "group_distinct",
        "field": "calculated_group_hash.keyword",
        "sort": {"data_source_relevance_filter": "asc"},
    },
    "queryset_for_first_time_indexing_filters": (
        MODEL_PARAMS["_default"]["queryset_for_indexing_filters"]
        & Q(sets__visible=True)
    ),
    "queryset_for_indexing_filters": (
        (
            (Q(indexed_at=None) | Q(need_to_index=True))
            | (
                Q(updated_at__gt=F("indexed_at"))
                | Q(sets__updated_at__max__gt=F("indexed_at"))
            )
        )
        & Q(has_visible_set=True)
    ),
    "range_fields": {"publish_year": "date_field_filter"},
    "search_fields": {
        "for_search": [
            "title^4",
            "creator_field^4",
            "truncated_description^2",
            "subject_field",
        ],
        "for_suggestions": ["title.suggestions"],
    },
    "search_system_filters": {
        "visible_filter": [True],
        "has_visible_set_filter": [True],
    },
    "search_system_sortby": {
        "_score": "desc",
        "data_source_relevance_filter": "asc",
        # "updated_at": "desc",
        # "pk": "desc",
    },
}
# Override date sorting for ContentResource
MODEL_PARAMS[ContentResource._meta.model_name]["sort_rules"].update(
    {"recent": {"date_field_filter": "desc"}, "-recent": {"date_field_filter": "asc"}}
)
MODEL_PARAMS["wagtail__harvester_contentresource"] = {
    **MODEL_PARAMS["_default"],
    "base_model_queryset": ContentResource.objects.select_related("data_source"),
    "extra_queryset_annotate_for_first_time_indexing": {
        "has_visible_set": Value(True, output_field=BooleanField())
    },
    "extra_queryset_annotate_for_indexing": {
        "has_visible_set": Exists(
            Set.objects.filter(contentresource=OuterRef("id")).visible()
        ),
        "calculated_group_hash": F("calculated_group_hash"),
        # https://docs.djangoproject.com/en/2.2/ref/models/expressions/#using-aggregates-within-a-subquery-expression
        "sets__updated_at__max": Subquery(
            Set.objects.filter(contentresource=OuterRef("id"))
            .visible()
            .order_by()
            .values("visible")
            .annotate(updated_at__max=Max("updated_at"))
            .values("updated_at__max"),
            output_field=DateTimeField(),
        ),
    },
    "group_by": {
        "aggs_name": "group_distinct",
        "field": "calculated_group_hash.keyword",
        "sort": {"data_source_relevance_filter": "asc"},
    },
    "queryset_for_first_time_indexing_filters": (
        MODEL_PARAMS["_default"]["queryset_for_indexing_filters"]
        & Q(sets__visible=True)
    ),
    "queryset_for_indexing_filters": (
        (
            (Q(indexed_at=None) | Q(need_to_index=True))
            | (
                Q(updated_at__gt=F("indexed_at"))
                | Q(sets__updated_at__max__gt=F("indexed_at"))
            )
        )
        & Q(has_visible_set=True)
    ),
    "range_fields": {"publish_year": "date_field_filter"},
    "search_fields": {
        "for_search": [
            "title^4",
            "creator_field^4",
            "truncated_description^2",
            "subject_field",
        ],
        "for_suggestions": ["title.suggestions"],
    },
    "search_system_filters": {
        "visible_filter": [True],
        "has_visible_set_filter": [True],
    },
    "search_system_sortby": {
        "_score": "desc",
        "data_source_relevance_filter": "asc",
        # "updated_at": "desc",
        # "pk": "desc",
    },
}
# Override date sorting for ContentResource
MODEL_PARAMS["wagtail__harvester_contentresource"]["sort_rules"].update(
    {"recent": {"date_field_filter": "desc"}, "-recent": {"date_field_filter": "asc"}}
)

MODEL_PARAMS[Collection._meta.model_name] = {
    **MODEL_PARAMS["_default"],
    "base_model_queryset": Collection.objects.select_related("owner"),
    "queryset_for_indexing_filters": (
        MODEL_PARAMS["_default"]["queryset_for_indexing_filters"]
        | Q(updated_at__gt=F("indexed_at"))
    ),
    "search_fields": {
        "for_search": ["title^4", "description^2", "data_source_name"],
        "for_suggestions": ["title.suggestions"],
    },
    "search_system_filters": {
        "visible": [True],
        "public": [True],
    },
    "search_system_sortby": {
        "_score": {},
        "home_site": "desc",
        "home_internal": "desc",
        "updated_at": "desc",
        "pk": "desc",
    },
}
MODEL_PARAMS[Collection._meta.model_name]["_source_fields"].update(
    {
        "for_search": ["pk", "collection_type"],
    }
)
MODEL_PARAMS[Collection._meta.model_name].update(
    {
        "queryset_for_first_time_indexing_filters": MODEL_PARAMS[
            Collection._meta.model_name
        ]["queryset_for_indexing_filters"]
    }
)

MODEL_PARAMS[Set._meta.model_name] = {
    **MODEL_PARAMS[Collection._meta.model_name],
    "base_model_queryset": Set.objects.select_related("data_source"),
}

MODEL_PARAMS[Exposition._meta.model_name] = {
    **MODEL_PARAMS["_default"],
    "base_model_queryset": Exposition.objects,
    "queryset_for_indexing_filters": (
        MODEL_PARAMS["_default"]["queryset_for_indexing_filters"]
        | Q(last_published_at__gt=F("indexed_at"))
        | Q(live=False)
    ),
    "search_fields": {
        "for_search": ["title^4", "description^2", "subject"],
        "for_suggestions": ["title.suggestions"],
    },
    "search_system_filters": {"live": [True], "expired": [False]},
}
MODEL_PARAMS[Exposition._meta.model_name].update(
    {
        "queryset_for_first_time_indexing_filters": MODEL_PARAMS[
            Exposition._meta.model_name
        ]["queryset_for_indexing_filters"]
    }
)
