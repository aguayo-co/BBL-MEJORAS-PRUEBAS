"""Define Cloud visualizations for expositions app."""
import json
from collections import defaultdict

from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import MultiFieldPanel, FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet

from .resource import Resource


@register_snippet
class Cloud(ClusterableModel):
    """Define an tag or terms Cloud model."""

    title = models.CharField(max_length=255, unique=True, verbose_name=_("Título"))
    subtitle = models.CharField(
        max_length=150, unique=True, verbose_name=_("Subtítulo"), null=True, blank=True
    )
    group_by = models.CharField(
        max_length=15,
        choices=(
            ("subject", _("Tema")),
            ("creator", _("Autor")),
            ("data_source", _("Fuente de datos")),
            ("date", _("Año de publicación")),
            ("type", _("Formato")),
        ),
        verbose_name=_("Agrupar por"),
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel("title"), FieldPanel("subtitle"), FieldPanel("group_by")],
            heading=_("Estructura"),
        ),
        InlinePanel("resources", min_num=1, label=_("Recursos")),
    ]

    @property
    def groups(self):
        """Group resources that contain the same value in the group_by attribute."""
        groups = defaultdict(list)
        for resource in self.resources.all():
            # Get from overridden fields
            value = getattr(resource, self.group_by, None)
            # Get from Resource Processed Data
            if value is None or value == "":
                value = getattr(resource.resource.processed_data, self.group_by)
            if self.group_by == "date" and hasattr(value, "year"):
                value = value.year
            # Subject items are dicts
            if isinstance(value, dict):
                for key in value.keys():
                    groups[key].append(resource)
                continue
            groups[value].append(resource)
        groups.default_factory = None
        return groups

    def json_groups(self):
        """Count items in groups for use in javascript."""
        json_groups = {
            # group: len(resources) for group, resources in self.groups.items()
            str(group): len(resources)
            for group, resources in self.groups.items()
        }
        return json.dumps(json_groups)

    class Meta:
        """Define some custom properties for Cloud."""

        verbose_name = _("Nube de Términos")
        verbose_name_plural = _("Nubes de Términos")

    def __str__(self):
        """Return the Cloud's name."""
        return self.title


class CloudResource(Resource):
    """Intermediate model that relates a Resource to a Cloud."""

    cloud = ParentalKey(Cloud, related_name="resources")
