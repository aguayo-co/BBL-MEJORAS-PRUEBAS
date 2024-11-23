"""Define Narrative visualizations for expositions app."""
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.blocks import StreamBlock
from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet

from expositions.editors import MiniEditor
from expositions.models.resource import Resource
from resources.wagtail.edit_handlers import CollapsibleMultiFieldPanel


@register_snippet
class Narrative(ClusterableModel):
    """Define an tag or terms Resource Narrative model."""

    title = models.CharField(max_length=255, unique=True, verbose_name=_("Título"))
    description = models.TextField(verbose_name=_("Descripción"))

    panels = [
        MultiFieldPanel(
            [FieldPanel("title"), FieldPanel("description")], heading=_("Definición")
        ),
        InlinePanel("resources", min_num=1, label=_("Recursos")),
    ]

    class Meta:
        """Define some custom properties for Narratives."""

        verbose_name = _("Narrativa")
        verbose_name_plural = _("Narrativas")

    def __str__(self):
        """Return the Resource Narrative's name."""
        return self.title


class NarrativeResource(Resource):
    """Intermediate model that relates a Resource to a ResourceNarrative."""

    resource_narrative = ParentalKey(Narrative, related_name="resources")
    related_text = StreamField(
        StreamBlock([("related_text", MiniEditor())], max_length=800, max_num=1),
        verbose_name=_("Texto Relacionado"),
        use_json_field=True
    )

    panels = [
        FieldPanel("resource"),
        FieldPanel("image"),
        FieldPanel("related_text"),
        CollapsibleMultiFieldPanel(
            [
                FieldPanel("title", widget=forms.TextInput),
                FieldPanel("description"),
                FieldPanel("creator", widget=forms.TextInput),
                FieldPanel("date"),
                FieldPanel("type"),
            ],
            heading=_("Corregir Campos del Recurso"),
            classname="collapsible collapsed",
        ),
    ]
