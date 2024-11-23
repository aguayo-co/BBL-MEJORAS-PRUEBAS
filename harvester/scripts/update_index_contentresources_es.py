import logging
from elasticsearch.helpers import scan, bulk

from search_engine import config as es_conf


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def run(params=None):
    ELASTICSEARCH_CLIENT = es_conf.ELASTICSEARCH_CLIENT
    index_name = 'wagtail__harvester_contentresource'  # Index name to update

    # Documents list with filter applied
    documents = list(scan(
        ELASTICSEARCH_CLIENT,
        index=index_name,
        query={
            "query": {
                "term": {
                    "has_visible_set_filter": False
                }
            }
        }
    ))

    # Action for to update matchs by document
    actions = [
        {
            '_op_type': 'update',
            '_index': index_name,
            '_id': document['_id'],
            'doc': {
                'has_visible_set_filter': True
            }
        }
        for document in documents
    ]

    success, failed = bulk(ELASTICSEARCH_CLIENT, actions)
    logger.info(
        "Parametro has_visible_set actualizado en %s documentos del indice %s",
        success,
        index_name
    )
    if len(failed) > 0:
      logger.info(
          "Error actualizando el Parametro has_visible_set en %s documentos del indice %s",
          failed,
          index_name
      )
