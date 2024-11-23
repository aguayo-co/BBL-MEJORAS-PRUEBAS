"""Elastic search frontend API helpers."""

import json
import logging

import requests
from constance import config
from django.conf import settings

from .. import config as es_conf

ELASTICSEARCH_CLIENT = es_conf.ELASTICSEARCH_CLIENT

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


#########################################
# Frontend API helper functions         #
#########################################

# Advanced search helpersv


def get_subqueries(boolean_queries):
    """
    Clasifica los queries para ser usados por elasticsearch.

    Divide los boolean queries según los 'or' operators.

    Clasifica los grupos de queries obtenidos según su ubicación en el
    query final de búsqueda de elasticsearch.
    """
    if boolean_queries is None:
        return None

    subquery_index = 0
    subqueries = [[]]
    for loop_index, boolean_query in enumerate(boolean_queries):
        if boolean_query and boolean_query["is_or"] and loop_index > 0:
            subquery_index += 1
            subqueries.append([])
            continue

        subqueries[subquery_index].append(boolean_query)

    return subqueries


def is_valid_boolean_queries(boolean_queries):
    """Check is boolean queries has valid queries."""
    if boolean_queries is None or not len(boolean_queries):
        return False

    empty_queries = 0
    for query in boolean_queries:
        if "q" in query and (query["q"].strip() == "" or query["q"] is None):
            empty_queries += 1

    if empty_queries and empty_queries == len(boolean_queries):
        return False

    return True


def add_should_subqueries(boolean_queries, search_query):
    """Añade todos los 'or' boolean queries al query principal."""
    for queries in boolean_queries:
        if queries:
            should_subquery = {"bool": {"must": [], "must_not": []}}
            must = should_subquery["bool"]["must"]
            must_not = should_subquery["bool"]["must_not"]
            for query in queries:
                if "q" in query and query["q"]:
                    if query["operator"] == "and":
                        add_elasticsearch_match_phrase_query(query, must)
                    if query["operator"] == "not":
                        add_elasticsearch_match_phrase_query(query, must_not)
            if must or must_not:
                search_query["bool"]["should"].append(should_subquery)


def add_elasticsearch_match_phrase_query(query, append_to_list):
    """Añade un 'term query' a la lista indicada."""
    append_to_list.append({"match_phrase": {query["field"]: query["q"]}})


# Search helpers


def get_elasticsearch_query(model, search_fields_key="for_search", **kwargs):
    """
    Arma un dict para realizar un query con filtros en elasticsearch.

    La variable `search_fields` es una lista de strings con los nombres de los campos
    que será utilizado para hacer la búsqueda

    Las variables `*_filters` son dict con el formato `field: value` usado para
    aplicar filtros a los resultados de búsqueda. La clave `field` es el nombre del
    campo del documento que se utilizará para filtrar los resultados de búsqueda con el
    `value` dado. El `value` debe ser una lista de strings.
    """
    search_text = kwargs.get("search_text")
    exact_search = kwargs.get("exact_search")
    user_filters = kwargs.get("user_filters")
    from_publish_year = kwargs.get("from_publish_year")
    to_publish_year = kwargs.get("to_publish_year")
    boolean_queries = kwargs.get("boolean_queries")

    main_bool_query = get_main_bool_query(
        model, search_fields_key, search_text, exact_search
    )

    search_filters = get_search_filters(
        model, user_filters, from_publish_year, to_publish_year
    )

    # Prepare final query
    search_query = {
        "bool": {
            "must": [
                {
                    "bool": {
                        "must": main_bool_query["must"],
                        "should": main_bool_query["should"]
                        + main_bool_query["boost_should"],
                    }
                }
            ],
            "filter": search_filters,
        }
    }

    if is_valid_boolean_queries(boolean_queries):
        search_query["bool"].update({"should": [], "minimum_should_match": 1})
        subqueries = get_subqueries(boolean_queries)
        add_should_subqueries(subqueries, search_query)

    return search_query


def get_main_bool_query(model, search_fields_key, search_text=None, exact_search=None):
    """Retorna el bool query del search text principal."""
    main_bool_query = {
        "must": [],
        "should": [],
        "boost_should": [],
    }

    if search_text is None:
        main_bool_query["must"].append({"match_all": {}})
    else:
        search_fields = es_conf.MODEL_PARAMS[model._meta.model_name]["search_fields"][
            search_fields_key
        ]
        multi_match = {
            "multi_match": {
                "type": "phrase",
                "query": search_text,
                "fields": search_fields,
            }
        }

        if exact_search:
            main_bool_query["must"].append(multi_match)
        else:
            main_bool_query["boost_should"].append(multi_match)
            main_bool_query["must"].append(
                {"simple_query_string": {"query": search_text, "fields": search_fields}}
            )

    return main_bool_query


def get_search_filters(
    model, user_filters=None, from_publish_year=None, to_publish_year=None
):
    """Arma un list con los filtros de la búsqueda."""
    search_filters = []

    system_filters = es_conf.MODEL_PARAMS[model._meta.model_name][
        "search_system_filters"
    ]

    if system_filters:
        for field, value in system_filters.items():
            search_filters.append({"terms": {field: value}})

    if user_filters:
        index_fields = es_conf.INDICES_CONFIG[es_conf.get_indice_name(model)][
            "mappings"
        ]["properties"]
        for field, value in user_filters.items():

            # Ignore field not mapping in the model index and empty values
            if field not in index_fields.keys() or value is None:
                continue

            # Check if index field is an analyzed text and use a keyword subfield
            if index_fields[field]["type"] == "text":
                field = get_keyword_subfield(index_fields, field)
                if field is None:
                    continue

            # Add filter
            search_filters.append({"terms": {field: value}})

    if from_publish_year or to_publish_year:
        field = es_conf.MODEL_PARAMS[model._meta.model_name]["range_fields"][
            "publish_year"
        ]

        if field:
            search_filters.append(
                {
                    "range": {
                        field: {
                            "gte": from_publish_year,
                            "lte": to_publish_year,
                            "format": "yyyy",
                        }
                    }
                }
            )

    return search_filters


def get_keyword_subfield(index_fields, field):
    """Obtiene un subfield type: 'keyword' de un field type 'text'."""
    if "fields" in index_fields[field]:
        for key, value in index_fields[field]["fields"].items():
            if value["type"] == "keyword":
                field += "." + key
                return field
    return None


def get_elasticsearch_collapse(model, sort=None):
    """Arma un dict para agrupar resultados en una búsqueda de elasticsearch.

    El argumento `sort` es una lista de dicts  con el formato `field: order`
    usada para aplicar reglas de ordenamiento a los elementos agrupados

    """
    groupby = es_conf.MODEL_PARAMS[model._meta.model_name]["group_by"]["field"]

    collapse = {}
    collapse["field"] = groupby
    collapse["inner_hits"] = {}
    collapse["inner_hits"]["name"] = "count"
    collapse["inner_hits"]["size"] = 0
    if sort:
        collapse["inner_hits"]["sort"] = []
        for field, order in sort.items():
            collapse["inner_hits"]["sort"].append({field: order})

    return collapse


def get_elasticsearch_distinct_field_count_aggs(model):
    """Arma un dict para contar resultados de una búsqueda después de agruparlos."""
    if es_conf.MODEL_PARAMS[model._meta.model_name]["group_by"]["aggs_name"]:
        return {
            es_conf.MODEL_PARAMS[model._meta.model_name]["group_by"]["aggs_name"]: {
                "cardinality": {
                    "field": es_conf.MODEL_PARAMS[model._meta.model_name]["group_by"][
                        "field"
                    ]
                }
            }
        }
    return {}


def search_with_elasticsearchpy(indexes_list, body=None, params=None):
    """Hacer una búsqueda con cuerpo usando el api de elasticsearchpy.

    EL argumento `body` es un dict con la estructura query dsl de elasticsearch
    https://www.elastic.co/guide/en/elasticsearch/reference/6.5/query-filter-context.html

    El argumento `params` es un dict de parametros para consumir el api de elasticsearch
    https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.Elasticsearch.search

    """
    # Execute search
    elasticsearch_response = ELASTICSEARCH_CLIENT.search(
        index=indexes_list, body=body, params=params
    )
    return elasticsearch_response


def search_with_requests(indexes_list, data):
    """Hacer una búsqueda con cuerpo usando la libreria requests.

    El argumento `data` es un dict con la estructura query dsl de elasticsearch
    https://www.elastic.co/guide/en/elasticsearch/reference/6.5/

    """
    indexes = ", ".join(indexes_list)
    url = (
        f"{settings.SEARCHBOX_SSL_URL_API}/{indexes}/_search?"
        "search_type=dfs_query_then_fetch"
    )
    headers = {"content-type": "application/json"}
    return requests.get(url, data=json.dumps(data), headers=headers).json()


def get_data_for_search_with_requests(model, **kwargs):
    """Arma un dict para usarlo como parametro `data` de en `search_with_requests`."""
    query_kwargs = {
        "search_text": kwargs.get("search_text"),
        "exact_search": kwargs.get("exact_search"),
        "user_filters": kwargs.get("filters"),
        "from_publish_year": kwargs.get("from_publish_year"),
        "to_publish_year": kwargs.get("to_publish_year"),
        "boolean_queries": kwargs.get("boolean_queries"),
    }
    pagination_start = kwargs.get("pagination_start", 0)
    pagination_size = kwargs.get("pagination_size", config.PAGE_SIZE)
    sort_by = kwargs.get("order_by")

    # Elasticsearch api query params
    query_params = {"query": get_elasticsearch_query(model, **query_kwargs)}
    if es_conf.MODEL_PARAMS[model._meta.model_name]["group_by"]["field"]:
        query_params["collapse"] = get_elasticsearch_collapse(model)
        query_params["aggs"] = get_elasticsearch_distinct_field_count_aggs(model)

    other_params = {}

    # Pagination
    other_params["from"] = pagination_start
    other_params["size"] = pagination_size

    # Returned fields
    other_params["_source"] = es_conf.MODEL_PARAMS[model._meta.model_name][
        "_source_fields"
    ]["for_search"]

    # Sorting
    other_params["sort"] = []
    if sort_by:
        other_params["sort"].append(
            es_conf.MODEL_PARAMS[model._meta.model_name]["sort_rules"][sort_by]
        )
    for field, value in es_conf.MODEL_PARAMS[model._meta.model_name][
        "search_system_sortby"  # pylint: disable=bad-continuation
    ].items():
        other_params["sort"].append({field: value})
    return {**query_params, **other_params}


def get_search_formatted_response(model, elasticsearch_response):
    """Arma un dict con el formato de resultados de búsqueda según el modelo."""
    response = {
        "result_list_id": [],
        "result_list_collection_type": [],
        "total_ungrouped_result": 0,
    }
    model_name = model._meta.model_name
    if "hits" in elasticsearch_response and elasticsearch_response["hits"]["total"]:
        for hit in elasticsearch_response["hits"]["hits"]:
            response["result_list_id"].append(hit["_source"]["pk"])
            if model_name == "collection":
                response["result_list_collection_type"].append(
                    hit["_source"]["collection_type"]
                )

        response["total_ungrouped_result"] = elasticsearch_response["hits"]["total"]

        if es_conf.MODEL_PARAMS[model_name]["group_by"]["field"]:
            response["total_grouped_result"] = elasticsearch_response["aggregations"][
                es_conf.MODEL_PARAMS[model_name]["group_by"]["aggs_name"]
            ]["value"]

    if "error" in elasticsearch_response:
        logger.error(elasticsearch_response)

    response.setdefault("total_grouped_result", response["total_ungrouped_result"])
    return response


# Suggestions helpers


def get_model_suggestions(model, search_text, **kwargs):
    """Obtiene las sugerencias de un texto de búsqueda de un modelo en específico."""
    elasticsearchpy_args = get_suggestions_args_for_search_with_elasticsearchpy(
        model, search_text, **kwargs
    )
    index_name = es_conf.get_indice_name(model)
    elasticsearch_response = search_with_elasticsearchpy(
        indexes_list=[index_name],
        body=elasticsearchpy_args["body"],
        params=elasticsearchpy_args["params"],
    )
    return get_suggestions_formatted_response(model, elasticsearch_response)


def get_suggestions_args_for_search_with_elasticsearchpy(model, search_text, **kwargs):
    """
    Arma un dict de `body` y `params` para `search_with_elasticsearchpy`.

    Este dict es para ser usado al traer sugerencias
    """
    query_kwargs = {
        "search_text": search_text,
        "user_filters": kwargs.get("filters"),
    }
    pagination_size = kwargs.get("pagination_size", 6)

    # Elasticsearchpy api request body
    body = {}
    body["query"] = get_elasticsearch_query(
        model, get_elasticsearch_query="for_suggestions", **query_kwargs
    )
    if es_conf.MODEL_PARAMS[model._meta.model_name]["group_by"]["field"]:
        body["collapse"] = get_elasticsearch_collapse(model)
        body["aggs"] = get_elasticsearch_distinct_field_count_aggs(model)

    # Elasticsearchpy api request params
    params = {}
    params["search_type"] = "dfs_query_then_fetch"

    # Pagination
    params["size"] = pagination_size

    # Returned fields
    params["_source"] = es_conf.MODEL_PARAMS[model._meta.model_name]["_source_fields"][
        "for_suggestions"
    ]

    # Sorting
    params["sort"] = []
    for field, value in es_conf.MODEL_PARAMS[model._meta.model_name][
        "search_system_sortby"  # pylint: disable=bad-continuation
    ].items():
        params["sort"].append({field: value})
    return {"body": body, "params": params}


def get_suggestions_formatted_response(model, elasticsearch_response):
    """Arma un dict con el formato de sugerencias según el modelo."""
    return [
        get_suggestion_format(model, suggestion)
        for suggestion in elasticsearch_response["hits"]["hits"]
    ]


def get_suggestion_format(model, element):
    """Arma un dict para el retorno formateado de las sugerencias."""
    source_field = es_conf.MODEL_PARAMS[model._meta.model_name]["_source_fields"][
        "for_suggestions"
    ]
    suggestion_format = {}
    suggestion_format["id"] = element["_id"]
    if isinstance(element["_source"][source_field], list):
        suggestion_format[source_field] = element["_source"][source_field][0]
    else:
        suggestion_format[source_field] = element["_source"][source_field]
    return suggestion_format


# Didyoumean helpers


def get_elasticsearch_suggest(model, search_text, is_term_suggest=False):
    """Trae sugerencias `didyoumean` de elasticsearch usando frases.

    Arma un dict para traer sugerencias `didyoumean` de elasticsearch usando frases.
    """
    suggest_block_name = es_conf.MODEL_PARAMS[model._meta.model_name]["didyoumean"][
        "suggest_block_name"
    ]
    # Elasticsearchpy api request phrase suggest body
    suggest = {"text": search_text}
    suggest[suggest_block_name] = {}
    if is_term_suggest:
        suggest[suggest_block_name]["term"] = {
            **es_conf.MODEL_PARAMS[model._meta.model_name]["didyoumean"][
                "term_suggest_params"
            ]
        }
    else:
        suggest[suggest_block_name]["phrase"] = {
            **es_conf.MODEL_PARAMS[model._meta.model_name]["didyoumean"][
                "phrase_suggest_params"
            ]
        }
        suggest[suggest_block_name]["phrase"]["collate"] = {
            "query": {"source": {"match_phrase": {"title": "{{suggestion}}"}}},
            "prune": True,
        }
    return suggest


def get_didyoumean_args_for_search_with_elasticsearchpy(
    model, search_text  # pylint: disable=bad-continuation
):
    """
    Crea dict para con `body` y `params` para `search_with_elasticsearchpy`.

    Este dict es para ser usado al traer un didyoumean
    """
    # Elasticsearchpy api request body
    body = {}
    is_term_suggest = len(search_text.split()) == 1
    body["suggest"] = get_elasticsearch_suggest(
        model, search_text, is_term_suggest=is_term_suggest
    )

    # Elasticsearchpy api request params
    params = {}
    params["search_type"] = "dfs_query_then_fetch"

    # Returned fields
    params["_source"] = es_conf.MODEL_PARAMS[model._meta.model_name]["_source_fields"][
        "for_didyoumean"
    ]

    # Sorting
    params["sort"] = []
    for field, value in es_conf.MODEL_PARAMS[model._meta.model_name][
        "search_system_sortby"  # pylint: disable=bad-continuation
    ].items():
        params["sort"].append({field: value})
    return {"body": body, "params": params}, is_term_suggest


def get_didyoumean_formatted_response(
    model, elasticsearch_response, is_term_suggest=False
):
    """Arma un dict con el formato de resultados de opciones para `didyoumean`."""
    if "suggest" in elasticsearch_response:
        options = elasticsearch_response["suggest"][
            es_conf.MODEL_PARAMS[model._meta.model_name]["didyoumean"][
                "suggest_block_name"
            ]
        ][0]["options"]
        if options:
            if is_term_suggest:
                return [
                    {k: v for k, v in option.items() if k in ["text", "highlighted"]}
                    for option in options
                ]
            return [
                {k: v for k, v in option.items() if k in ["text", "highlighted"]}
                for option in options
                if option["collate_match"] is True
            ]
    return None
