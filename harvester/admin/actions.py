"""Define admin actions for Harvester app."""

from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.db.models import Count
from django.forms import Form, ModelChoiceField
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task

from harvester.models import Set
from resources.models import TimestampModel


def show(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Mark given elements as visible."""
    modeladmin.message_user(
        request,
        _(
            "Programado el marcado de los elementos seleccionados y sus objetos relacionados como Visibles."
        ),
        messages.SUCCESS,
    )
    async_task(
        "harvester.admin.tasks.hide_show_queryset_task",
        queryset,
        "show",
        group=f"Marcado de registros como visibles",
        task_name="Marcado de registros como visibles",
    )


def hide(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Mark given elements as invisible."""
    modeladmin.message_user(
        request,
        _(
            "Programado el marcado de los elementos seleccionados y sus objetos relacionados como No-Visibles."
        ),
        messages.SUCCESS,
    )
    async_task(
        "harvester.admin.tasks.hide_show_queryset_task",
        queryset,
        "hide",
        group=f"Marcado de registros como No-Visibles",
        task_name="Marcado de registros como No-Visibles",
    )


def set_home_site(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Set home_site flag form elements."""
    queryset.update(home_site=True, updated_at=timezone.now())


def unset_home_site(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Remove home_site flag form elements."""
    queryset.update(home_site=False, updated_at=timezone.now())


def set_home_internal(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """Set home_internal flag form elements."""
    queryset.update(home_internal=True, updated_at=timezone.now())


def unset_home_internal(
    modeladmin, request, queryset
):  # pylint: disable=unused-argument
    """Remove home_internal flag form elements."""
    queryset.update(home_internal=False, updated_at=timezone.now())


# Custom Actions Names
show.short_description = _(
    "Marca los %(verbose_name_plural)s seleccionados y sus dependientes como visibles"
)
hide.short_description = _(
    "Marca los %(verbose_name_plural)s seleccionados y sus dependientes como no-visibles"
)
set_home_site.short_description = _(
    "Marca los %(verbose_name_plural)s seleccionados como destacados en el home"
    " principal"
)
unset_home_site.short_description = _(
    "Marca los %(verbose_name_plural)s seleccionados como no destacados en el home"
    " principal"
)
set_home_internal.short_description = _(
    "Marca los %(verbose_name_plural)s seleccionados como destacados en el home interno"
)
unset_home_internal.short_description = _(
    "Marca los %(verbose_name_plural)s seleccionados como no destacados en el home"
    " interno"
)


def mark_for_delete_in_background(modeladmin, request, queryset):
    """Define action which Mark items to be deleted in background."""
    opts = modeladmin.model._meta
    app_label = opts.app_label

    count = queryset.count()

    # The user has already confirmed the deletion.
    # Update objects and return None to display the change list view again.
    if request.POST.get("post"):
        if count:
            if issubclass(modeladmin.model, TimestampModel):
                queryset.update(to_delete=True)
                modeladmin.message_user(
                    request,
                    _(
                        "Programada eliminación en segundo plano de %(count)d %(items)s y"
                        " sus objetos relacionados."
                    )
                    % {"count": count, "items": model_ngettext(modeladmin.opts, count)},
                    messages.SUCCESS,
                )
            else:
                modeladmin.message_user(
                    request,
                    _(
                        "No es posible eliminar estos objetos en segundo plano, por favor utilice el borrado estandar"
                    ),
                    messages.WARNING,
                )
        # Return None to display the change list page again.
        return None

    objects_name = model_ngettext(queryset)

    context = {
        **modeladmin.admin_site.each_context(request),
        "title": _("Está seguro?"),
        "objects_name": str(objects_name).title(),
        "queryset": queryset,
        "opts": opts,
        "count_message": f"{count} {model_ngettext(modeladmin.opts, count)}",
        "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
        "select_across": request.POST.get("select_across", 0),
        "index": request.POST.get("index", 0),
        "selected_items": queryset.values_list("pk", flat=True)[:100],
        "media": modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(
        request,
        "%s/delete_selected_in_background_confirmation.html" % "harvester",
        context,
    )


mark_for_delete_in_background.allowed_permissions = ("delete",)
mark_for_delete_in_background.short_description = _(
    "Eliminar %(verbose_name_plural)s seleccionado/s en segundo plano"
)


class SetSelectionForm(Form):
    """Form to select a Set."""

    def __init__(self, data_source_id, *args, **kwargs):
        """Add Set to Form."""
        super().__init__(*args, **kwargs)
        self.fields["set"] = ModelChoiceField(
            queryset=Set.objects.filter(data_source_id=data_source_id),
            label=Set._meta.verbose_name.title(),
            required=True,
        )


def mass_change_resource_set(modeladmin, request, queryset):
    """Mass change a :ContentResource: object related `Set` in background."""
    data_source_ids = queryset.values_list("data_source_id", flat=True).annotate(
        Count("data_source_id")
    )

    if data_source_ids.count() > 1:
        modeladmin.message_user(
            request,
            _(
                "Sólo puede modificar el Set a recursos seleccionados que pertenezcan a la misma Fuente. Ha seleccionado"
                " recursos pertenecientes a diferentes fuentes: (%(data_source_names)s)."
            )
            % {
                "data_source_names": ", ".join(
                    set(queryset.values_list("data_source__name", flat=True))
                )
            },
            messages.ERROR,
        )
        return None

    data_source_id = data_source_ids.first()
    objects_name = model_ngettext(queryset).title()

    if request.POST.get("post"):
        form = SetSelectionForm(data_source_id, request.POST)
        if form.is_valid():
            new_set = form.cleaned_data["set"]
            async_task(
                "harvester.tasks.mass_change_resource_set_task",
                queryset.values_list("pk", flat=True),
                data_source_id,
                new_set,
            )

            message = _(
                "Se ha programado el cambio en segundo plano de %(count)d %(objects_name)s a la Colección Institucional"
                " '%(set)s'"
            ) % {
                "set": new_set.name,
                "count": queryset.count(),
                "objects_name": objects_name,
            }
            modeladmin.message_user(request, message, messages.SUCCESS)
            return None
    else:
        form = SetSelectionForm(data_source_id)

    opts = modeladmin.model._meta
    app_label = opts.app_label

    context = {
        **modeladmin.admin_site.each_context(request),
        "title": _("Cambiar Colección Institucional en segundo plano"),
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
        request, "%s/mass_change_resource_set.html" % app_label, context
    )


mass_change_resource_set.short_description = _(
    "Asignar Colección Institucional en segundo plano a %(verbose_name_plural)s seleccionado/s"
)
