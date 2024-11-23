"""Additional helper tags for menu handling."""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_visible_submenu_items(context, items):
    """Verifies that a submenu list has one or more visible items."""
    show_submenu = False
    for item in items:
        if (
            not item.get_view_restrictions().count()
            or context["request"].user.is_authenticated
        ):
            show_submenu = True
    return show_submenu
