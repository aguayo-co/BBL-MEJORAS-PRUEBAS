"""
Make debugging inspecting variables Django templates easier.

Example:

    {% load inspectors %}

    {{ object|inspect }}

"""

from pprint import pformat

from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter(is_safe=True)
def inspect(value, tag="pre"):
    """Print the objects properties and methods."""
    try:
        string = format_html("<{}>{}</{}>", tag, pformat(value), tag)
    except Exception as exception:  # pylint: disable=broad-except
        string = "Error in formatting: %s: %s" % (
            exception.__class__.__name__,
            exception,
        )

    vars_list = {}
    for item in dir(value):
        try:
            if item.startswith("_"):
                continue

            attribute = getattr(value, item)
            if callable(attribute):
                continue

            vars_list[item] = attribute
        except AttributeError:
            pass

    try:
        vars_info = format_html("<{}>{}</{}>", tag, pformat(vars_list), tag)
    except Exception as exception:  # pylint: disable=broad-except
        vars_info = "Error in formatting: %s: %s" % (
            exception.__class__.__name__,
            exception,
        )

    return string + vars_info
