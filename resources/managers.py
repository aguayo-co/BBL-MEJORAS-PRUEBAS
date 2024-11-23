"""Define Model Managers for Resources app."""

from django.db import models


class SelectRelatedManager(models.Manager):
    """Manager that uses (select|prefetch)_related on all queries by default."""

    def __init__(self, select_related=None, prefetch_related=None):
        """Save (select|prefetch)_related properties."""
        super().__init__()
        self._select_related = select_related
        self._prefetch_related = prefetch_related

    def get_queryset(self):
        """Apply (select|prefetch)_related to queryset."""
        queryset = super().get_queryset()

        if self._select_related:
            queryset = queryset.select_related(*self._select_related)

        if self._prefetch_related:
            queryset = queryset.prefetch_related(*self._prefetch_related)

        return queryset
