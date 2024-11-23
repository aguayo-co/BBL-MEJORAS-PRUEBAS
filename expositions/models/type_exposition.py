from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.snippets.models import register_snippet


@register_snippet
class TypeExposition(ClusterableModel):
    """The snippet for Exposure Types is created"""

    name = models.CharField(
        max_length=255, verbose_name=_("Nombre del tipo de exposición")
    )

    panels = [
        MultiFieldPanel([FieldPanel("name")]),
    ]

    class Meta:
        """Define some custom properties for Exposure Types"""

        verbose_name = _("Tipo de exposición")
        verbose_name_plural = _("Tipos de exposición")

    def __str__(self):
        """Return the Resource type's name."""
        return self.name
