"""Additional helper tags for resources app."""

import os
import urllib.parse

from django import template
from django.conf import settings
from django.forms.boundfield import BoundField
from django.utils.translation import gettext_lazy as _

from expositions.models import Exposition
from expositions.models.pages import QuestionPage
from harvester.models import CollaborativeCollection, Collection, Set

register = template.Library()


@register.filter()
def pager_range(pager, shift=0):
    """
    Return range with `shift` items from the current page.

    `pager` should be a Page object.
    https://docs.djangoproject.com/en/2.2/topics/pagination/#page-objects

    `shift` is the number of element to show from the current page.
    """
    total_pages = pager.paginator.num_pages
    current_page = pager.number

    start = min(current_page, current_page + shift)
    start = max(1, start)

    stop = max(current_page, current_page + shift)
    stop = min(total_pages, stop)

    if shift > 0:
        start += 1
        stop += 1

    return range(start, stop)


@register.simple_tag(takes_context=True)
def url_params(context, *args):
    """
    Modify and print existing url params as string.

    If no arguments are given, current query is returned.
    If arguments are given, odd arguments are used as keys and even arguments
    are used as values for the previous one (the key)

    Example:
    {% url_params 'page' 2 'color' 'red' 'remove_me' None %}
    page=2&color=red

    """
    args_count = len(args)
    if args_count % 2 > 0:
        raise ValueError("Number of arguments must be odd, %s given." % args_count)

    # Convert list into dict with odd elements as keys and even elements as values
    new_params = {args[i]: args[i + 1] for i in range(0, len(args), 2)}

    params = context["request"].GET.copy()

    # Replace existing values.
    for key, value in new_params.items():
        if value is not None:
            params[key] = value
            continue

        try:
            params.pop(key)
        except KeyError:
            pass

    return params.urlencode()


@register.simple_tag(takes_context=True)
def build_absolute_uri(context, url=None, request=None):
    """Return the fully qualified URL for the passed URL."""
    request_instance = None
    if request is not None and request != "":
        request_instance = request
    if hasattr(context, "request") and request_instance is None:
        request_instance = context.request
    if hasattr(context.flatten(), "request") and request_instance is None:
        request_instance = context.flatten().request

    if request_instance is not None and request_instance != "":
        return request_instance.build_absolute_uri(url)
    return urllib.parse.urljoin("https://www.bibliotecadigitaldebogota.gov.co", url)


@register.simple_tag(takes_context=False)
def get_boolean_operator_first_letter(index, forms):
    """Return a boolean operator firs letter."""
    if index - 1 <= 0:
        return _("Y")
    else:
        last_index = index - 1
        if BoundField(
            forms[last_index], forms[last_index].fields["is_or"], "is_or"
        ).value():
            return _("O")
        return _("Y")


@register.simple_tag(takes_context=False)
def get_boolean_operator_label(value):
    """Return a boolean operator `operator label`."""
    if value == "and":
        return _("con")
    if value == "not":
        return _("sin")


@register.simple_tag(takes_context=False)
def get_boolean_operator_field_label(key):
    """Return the label from `field` field."""
    if key is None:
        return None

    labels = {
        "creator_field": _("autor"),
        "title": _("título"),
        "publisher": _("publicador"),
        "subject_field": _("tema"),
        "description": _("descripción"),
    }
    return labels[key]


@register.filter()
def has_boolean_operator_forms(boolean_operator_formset):
    """Verify if boolean_operator_formset has valid forms."""
    if boolean_operator_formset is None:
        return False

    if not boolean_operator_formset.data:
        return False

    if not boolean_operator_formset.forms:
        return False

    for index, form in enumerate(boolean_operator_formset.forms):
        is_or = BoundField(form, form.fields["is_or"], "is_or").value()
        q = BoundField(form, form.fields["q"], "q").value()

        if index == 0 and (is_or is True or q == "" or q is None):
            return False

    return True


@register.filter
def get_meta(value, attribute=None):
    """Get object _meta."""
    if attribute:
        return getattr(value._meta, attribute)
    return value._meta


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def negate(boolean):
    return not boolean


@register.filter
def get_static_rel_path(full_path):
    if full_path:
        non_static_path = os.path.join(settings.BASE_DIR, "resources", "static")
        return os.path.relpath(full_path, non_static_path)
    return None


@register.filter
def get_selected_option_label(select_form_field):
    for choice in select_form_field.subwidgets:
        if choice.data["selected"]:
            return choice.data["label"]


@register.filter
def get_collection_name(select_form_field):
    return Collection.objects.get(pk=select_form_field.data).title


@register.filter
def is_collection(object):
    """Check if an object is a collection instance."""
    if object._meta.model_name in [
        Collection._meta.model_name,
        Set._meta.model_name,
        CollaborativeCollection._meta.model_name,
    ]:
        return True
    return False


@register.filter
def is_exposition(object):
    """Check if an object is a exposition instance."""
    if object._meta.model_name in [
        Exposition._meta.model_name,
    ]:
        return True
    return False


@register.filter
def is_help_center_answer(object):
    """Check if an object is a help center answer instance."""
    if object._meta.model_name in [
        QuestionPage._meta.model_name,
    ]:
        return True
    return False
