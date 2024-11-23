from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel
)
from wagtail.snippets.models import register_snippet


@register_snippet
class Sidebar(ClusterableModel):

    name = models.CharField(max_length=255, verbose_name=_("Nombre"))

    panels = [
        FieldPanel("name"),
        InlinePanel("related_themes", min_num=1, label=_("Temas relacionados")),
        InlinePanel("related_question", min_num=1, label=_("Preguntas relacionadas")),
    ]

    def __str__(self):
        """A readable representation."""
        return self.name

    class Meta:
        verbose_name = _("Sidebar")
        verbose_name_plural = _("Sidebars")
