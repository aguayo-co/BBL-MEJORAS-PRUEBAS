"""Define WagTail snippets for expositions app."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class DomainsPassModel(ClusterableModel):
    """Model to know the domains that will not go through the url processor."""

    name = models.CharField(
        verbose_name=_("Nombre"), max_length=256, null=True, blank=False
    )
    domain = models.URLField(
        verbose_name=_("Dominio"), max_length=256, null=True, blank=False
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("domain"),
    ]

    class Meta:
        """Define some custom properties for DomainsPassModel."""

        verbose_name = _("Dominio")
        verbose_name_plural = _("Dominios")

    def __str__(self):
        """Return the gallery name."""
        return self.name
