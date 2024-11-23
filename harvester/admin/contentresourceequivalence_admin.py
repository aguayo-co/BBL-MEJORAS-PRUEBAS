"""Define admin interfaces for :model:`harvester.ContentResourceEquivalence`."""

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.db.models import Count
from django.forms import Form
from django.forms.models import ModelChoiceField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateResponse
from import_export.admin import ImportExportActionModelAdmin, ImportExportModelAdmin

from ..models import ContentResourceEquivalence, Equivalence
from . import ExportInBackgroundMixin
from .import_export_resources import ContentResourceEquivalenceIEResource


class EquivalenceSelectionForm(Form):
    """Form to select an equivalence."""

    def __init__(self, field, *args, **kwargs):
        """Add equivalence field to form."""
        super().__init__(*args, **kwargs)
        self.fields["equivalence"] = ModelChoiceField(
            queryset=Equivalence.objects.filter(field=field),
            label=Equivalence._meta.verbose_name.title(),
            required=True,
        )


def mass_assign_equivalence(modeladmin, request, queryset):
    """Mass assign a :model:`harvester.Equivalence`."""
    fields = queryset.values_list("field", flat=True).annotate(Count("field"))
    if fields.count() > 1:
        modeladmin.message_user(
            request,
            _(
                "Sólo puede asignar equivalencias de un mismo tipo. Seleccionaste"
                " más de un tipo de campo: (%(fields)s)."
            )
            % {"fields": ", ".join(set(queryset.values_list("field", flat=True)))},
            messages.ERROR,
        )
        return None

    field = fields.first()
    objects_name = model_ngettext(queryset).title()

    if request.POST.get("clear"):
        queryset.update(equivalence=None, updated_at=timezone.now())
        message = _(
            "Equivalencia desasignada de forma correcta a"
            " %(count)d %(objects_name)s."
        ) % {"count": queryset.count(), "objects_name": objects_name}
        modeladmin.message_user(request, message, messages.SUCCESS)
        return None

    if request.POST.get("post"):
        form = EquivalenceSelectionForm(field, request.POST)
        if form.is_valid():
            equivalence = form.cleaned_data["equivalence"]
            queryset.update(equivalence=equivalence, updated_at=timezone.now())
            message = _(
                "Equivalencia '%(equivalence)s' asignada de forma correcta a"
                " %(count)d %(objects_name)s."
            ) % {
                "equivalence": equivalence.name,
                "count": queryset.count(),
                "objects_name": objects_name,
            }
            modeladmin.message_user(request, message, messages.SUCCESS)
            return None
    else:
        form = EquivalenceSelectionForm(field)

    opts = modeladmin.model._meta
    app_label = opts.app_label

    context = {
        **modeladmin.admin_site.each_context(request),
        "title": _("Asignar equivalencia"),
        "queryset": queryset,
        "objects_name": objects_name,
        "opts": opts,
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "selected_ids": request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
        "select_across": int(request.POST.get("select_across", "0")),
        "index": int(request.POST.get("index", "0")),
        "form": form,
        "media": modeladmin.media,
    }

    # Display the equivalence selection page.
    return TemplateResponse(
        request, "%s/mass_assign_equivalence.html" % app_label, context
    )


mass_assign_equivalence.allowed_permissions = ("change",)
mass_assign_equivalence.short_description = _(
    "Modificar equivalencia de %(verbose_name_plural)s seleccionado/s"
)


@admin.register(ContentResourceEquivalence)
class ContentResourceEquivalenceAdmin(
    ExportInBackgroundMixin, ImportExportActionModelAdmin, admin.ModelAdmin
):
    """Define admin integration for Content Resource Equivalences model."""

    actions = [
        mass_assign_equivalence,
        "export_admin_action",
    ]

    list_display = [
        "original_value",
        "field",
        "equivalence_name",
        "resources__count",
        "updated_at",
        "created_at",
    ]
    list_filter = ["field", "equivalence"]
    readonly_fields = ["original_value", "field"]
    search_fields = ["original_value"]
    resource_class = ContentResourceEquivalenceIEResource

    def resources__count(self, obj):
        """Return content_resource count."""
        return obj.resources_count

    resources__count.short_description = _("Número de recursos")
    resources__count.admin_order_field = "resources_count_cached"

    def equivalence_name(self, obj):
        """Return name of equivalence if one exists."""
        return obj.equivalence.name if obj.equivalence else None

    equivalence_name.short_description = _("equivalencia")
    equivalence_name.admin_order_field = "equivalence__name"

    def has_add_permission(self, request):
        """
        Disallow add.

        Posible values are created automatically when found.
        """
        return False

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Alter form to limit options for equivalence based on field."""
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        if obj and obj.field:
            form.base_fields["equivalence"].limit_choices_to = {"field": obj.field}
        return form
