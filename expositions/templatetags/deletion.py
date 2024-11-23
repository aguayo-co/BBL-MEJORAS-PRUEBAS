"""Template tags for Exposition app."""
from django import template
from django.db.models.deletion import Collector, ProtectedError

register = template.Library()


@register.filter()
def can_delete(obj):
    """Check if a wagtail model can be deleted."""
    return len(related_objects(obj)) == 0


@register.filter()
def related_objects(obj):
    """List all related objects of an object."""
    collector = Collector(using="default")
    try:
        collector.collect([obj])
    except ProtectedError as error:
        return error.protected_objects
    return []
