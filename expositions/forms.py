"""Define forms for Expositions app."""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms import WagtailAdminModelForm

from harvester.forms.fields import EquivalenceMultipleChoiceField
from resources.forms import FiltersForm


class ExpositionFilters(FiltersForm):
    """Filters for Exposition querysets."""

    FIELDS_LOOKUPS = {"subject": "subject__in"}
    subject = EquivalenceMultipleChoiceField(
        label=_("Tema"), field="subject", required=False
    )


class ExpositionMapForm(WagtailAdminModelForm):
    """Expositions map custom form."""

    def clean(self):
        """Make bounds required if image exists."""
        image = self.cleaned_data.get("image")
        if image:
            # validate if image exists
            bounds = {
                "image_top_corner_bound_latitude": self.cleaned_data.get(
                    "image_top_corner_bound_latitude"
                ),
                "image_top_corner_bound_longitude": self.cleaned_data.get(
                    "image_top_corner_bound_longitude"
                ),
                "image_bottom_corner_bound_latitude": self.cleaned_data.get(
                    "image_bottom_corner_bound_latitude"
                ),
                "image_bottom_corner_bound_longitude": self.cleaned_data.get(
                    "image_bottom_corner_bound_longitude"
                ),
            }
            for field, value in bounds.items():
                if value is None:
                    self.errors[field] = self.error_class(
                        [_("Si has seleccionado una imagen este campo es requerido")]
                    )
        return self.cleaned_data
