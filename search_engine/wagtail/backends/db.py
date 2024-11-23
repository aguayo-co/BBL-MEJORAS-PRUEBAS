"""Define a WagTail search backend compatible with postgres ArrayField."""
from django.db import models
from wagtail.search import index
from wagtail.search.backends.db import (
    DatabaseSearchBackend,
    DatabaseSearchQueryCompiler,
)


class ArraySearchField(index.SearchField):
    """Search field for WagTail compatible with Postgres Array fields."""

    def __init__(self, field_name, array_index=None, **kwargs):
        """Set the lookup name for the field, and pass to parent."""
        super().__init__(field_name, **kwargs)
        self.field_lookup = (
            field_name if array_index is None else f"{field_name}__{array_index}"
        )


class ArrayDatabaseSearchQueryCompiler(DatabaseSearchQueryCompiler):
    """Search query compiler for WagTail compatible with ArraySearchField."""

    def __init__(self, *args, **kwargs):
        """Store field lookups after executing parent init."""
        super().__init__(*args, **kwargs)
        self.fields_lookups = list(self.get_fields_lookups())

    def get_fields_lookups(self):
        """Get the field lookups to be used for this query."""
        if self.fields:
            yield self.fields

        for field in self.queryset.model.get_searchable_search_fields():
            yield getattr(field, "field_lookup", field.field_name)

    def build_single_term_filter(self, term):
        """Return search filters for `term`."""
        term_query = models.Q()
        for field_name in self.fields_lookups:
            term_query |= models.Q(**{field_name + "__icontains": term})
        return term_query


class ArrayDatabaseSearchBackend(DatabaseSearchBackend):
    """WagTail search database backend compatible with ArraySearchField."""

    query_compiler_class = ArrayDatabaseSearchQueryCompiler


SearchBackend = ArrayDatabaseSearchBackend
