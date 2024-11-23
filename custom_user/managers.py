"""Define managers for CustomUSer app."""

from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from wagtail.search.queryset import SearchableQuerySetMixin

from resources.managers import SelectRelatedManager


class UserQuerySet(SearchableQuerySetMixin, models.QuerySet):
    """Extend Queryset with Wagtail search functionality."""


class UserManager(SelectRelatedManager, DjangoUserManager.from_queryset(UserQuerySet)):
    """
    Define a custom User manager.

    This manager allows for WagTail search functionality and
    receives (select|prefetch)_related. arguments
    """
