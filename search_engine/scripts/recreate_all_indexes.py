"""Script for `runscript recreate_all_indexes`."""
from ..elasticsearch import recreate_all_indexes


def run():
    """Recreate all indexes for ElasticSearch."""
    recreate_all_indexes()
