"""Define admin filters for the Harvester app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import ContentResourceEquivalence


class EquivalenceMappingFilter(admin.ListFilter):
    """Filter a queryset by equivalences."""

    title = _("Mapeos")

    def __init__(self, request, params, model, model_admin):
        """Capture filter values."""
        super().__init__(request, params, model, model_admin)
        self.model = model
        self.mappings_parameters = {
            field: f"{field}__mapping" for field in self.model.FIELDS_WITH_EQUIVALENCES
        }
        for field, param in self.mappings_parameters.items():
            if param in params:
                value = params.pop(param)
                self.used_parameters[field] = value

    def choices(self, changelist):
        """Return an option to clear the filter."""
        yield {
            "selected": False,
            "query_string": changelist.get_query_string(
                remove=self.expected_parameters()
            ),
            "display": _("Quitar filtro"),
        }
        for content_resource_equivalence in ContentResourceEquivalence.objects.filter(
            id__in=self.used_parameters.values()
        ):
            yield {
                "selected": True,
                "query_string": changelist.get_query_string(
                    remove=content_resource_equivalence.field
                ),
                "display": content_resource_equivalence.original_value,
            }

    def has_output(self):
        """Return True if a filter is active."""
        return bool(self.used_parameters)

    def expected_parameters(self):
        """List the posible parameters this filter accepts."""
        return self.mappings_parameters.values()

    def queryset(self, request, queryset):
        """Filter the queryset using a Subquery of the model id."""
        for param, value in self.used_parameters.items():
            field = getattr(self.model, param).field
            queryset = queryset.filter(
                id__in=field.related_model.objects.filter(id=value).values(
                    f"{param}equivalencerelation__contentresource"
                )
            )

        return queryset
