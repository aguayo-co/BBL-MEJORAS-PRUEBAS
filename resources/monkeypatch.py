"""Do Monkeypatch for resources app."""

from django.contrib.admin import utils
from django.utils.html import format_html, format_html_join

django_display_for_value = utils.display_for_value


def display_for_value(value, empty_value_display, boolean=False):
    """
    Replace how Django prints arrays and tuples in admin.

    Print list and tuples as <ul> in Django admin.
    Did not find a better way. :(
    """

    if not boolean and isinstance(value, (list, tuple)):
        list_values = format_html_join("", "<li>{}</li>", ([str(v)] for v in value))
        return format_html("<ul>{}</ul>", list_values)

    return django_display_for_value(value, empty_value_display, boolean)


utils.display_for_value = display_for_value
