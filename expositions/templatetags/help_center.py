"""Template tags for Exposition app."""
from django import template

from expositions.models import Tooltip

register = template.Library()


@register.filter()
def get_tooltip(tooltip_name):
    """Check if a wagtail model can be deleted."""
    return Tooltip.objects.filter(page=tooltip_name).first()
