"""Additional helper tags for resources app."""
from django import template
from django.contrib.admin.utils import display_for_field, lookup_field
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import ManyToManyRel
from django.template.defaultfilters import linebreaksbr
from django.utils.html import conditional_escape

register = template.Library()


@register.filter()
def field_contents(admin_field):
    """
    Render fields as list if possible.

    When there is no custom rendering, return default field content.
    """
    field, obj, model_admin = (
        admin_field.field["field"],
        admin_field.form.instance,
        admin_field.model_admin,
    )

    try:
        model_field, attr, value = lookup_field(field, obj, model_admin)
    except (AttributeError, ValueError, ObjectDoesNotExist):
        return conditional_escape(admin_field.empty_value_display)
    else:
        if field not in admin_field.form.fields and model_field is not None:
            if (
                isinstance(model_field.remote_field, ManyToManyRel)
                and value is not None
            ):
                value = list(map(str, value.all()))
            result_repr = display_for_field(
                value, model_field, admin_field.empty_value_display
            )
            result_repr = linebreaksbr(result_repr)
            return conditional_escape(result_repr)

    return admin_field.contents()
