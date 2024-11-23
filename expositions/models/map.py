"""Define Map visualization for expositions app."""
from django.db import models
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.blocks import CharBlock, DecimalBlock, TextBlock, ListBlock
from wagtail.fields import StreamField
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet

from expositions.edit_handlers import FixedObjectList
from expositions.forms import ExpositionMapForm
from expositions.models.resource import (
    Milestone,
    Resource,
    MilestoneComponent,
    ResourceComponent,
)
from resources.fields import LatitudeField, LongitudeField


ZOOM_LEVELS = [(level, level) for level in range(0, 20)]


class MapMilestoneComponent(MilestoneComponent):
    """A Milestone that belongs to a Map."""

    title = CharBlock(max_length=60, label=_("Título"))
    latitude = DecimalBlock(
        label="Latitud", max_value=90, min_value=-90, max_digits=8, decimal_places=6
    )
    longitude = DecimalBlock(
        label="Longitud", max_value=180, min_value=-180, max_digits=9, decimal_places=6
    )
    place = TextBlock(label=_("Lugar"))
    pin_image = ImageChooserBlock(
        required=False,
        label=_("Icono del Pin"),
    )
    resources = ListBlock(ResourceComponent(), label=_("Recursos"))

    class Meta:
        """Define some custom properties for Timeline."""

        label = _("Hito de Mapa")
        icon = "site"


@register_snippet
class Map(ClusterableModel):
    """Define an Map model."""

    title = models.CharField(max_length=255, unique=True, verbose_name=_("Título"))
    description = models.TextField(verbose_name=_("Descripción"))
    center_at_latitude = LatitudeField(verbose_name=_("Latitud Inicio"))
    center_at_longitude = LongitudeField(verbose_name=_("Longitud Inicio"))
    min_zoom_level = models.IntegerField(
        choices=ZOOM_LEVELS, verbose_name=_("Zoom Mínimo")
    )
    max_zoom_level = models.IntegerField(
        choices=ZOOM_LEVELS, verbose_name=_("Zoom Máximo")
    )
    image = models.ForeignKey(
        get_image_model(),
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("Imagen de Fondo"),
    )
    image_top_corner_bound_latitude = LatitudeField(
        verbose_name=_("Latitud de esquina límite superior izquierda de imagen"),
        blank=True,
        null=True,
    )
    image_top_corner_bound_longitude = LongitudeField(
        verbose_name=_("Longitud de esquina límite superior izquierda de imagen"),
        blank=True,
        null=True,
    )
    image_bottom_corner_bound_latitude = LatitudeField(
        verbose_name=_("Latitud de esquina límite inferior derecha de imagen"),
        blank=True,
        null=True,
    )
    image_bottom_corner_bound_longitude = LongitudeField(
        verbose_name=_("Longitud de esquina límite inferior derecha de imagen"),
        blank=True,
        null=True,
    )

    milestones_content = StreamField(
        verbose_name="Hitos de Mapa",
        block_types=[("map_milestone", MapMilestoneComponent())],
        default=list,
        use_json_field=True
    )

    custom_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("description"),
                FieldRowPanel(
                    [
                        FieldPanel("center_at_latitude"),
                        FieldPanel("center_at_longitude"),
                    ]
                ),
                FieldPanel("min_zoom_level"),
                FieldPanel("max_zoom_level"),
                FieldPanel("image"),
                FieldRowPanel(
                    [
                        FieldPanel("image_top_corner_bound_latitude"),
                        FieldPanel("image_top_corner_bound_longitude"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("image_bottom_corner_bound_latitude"),
                        FieldPanel("image_bottom_corner_bound_longitude"),
                    ]
                ),
            ],
            heading=_("Estructura"),
        ),
        FieldPanel("milestones_content"),
        # MapMilestoneInlineCreator(
        # "milestones", min_num=1, max_num=10, label=_("Hitos")
        # ),
    ]

    base_form_class = ExpositionMapForm
    edit_handler = FixedObjectList(custom_panels, hide_on_add=("milestones",))

    class Meta:
        """Define some custom properties for Map."""

        verbose_name = _("Mapa")
        verbose_name_plural = _("Mapas")

    def __str__(self):
        """Return the Map's name."""
        return self.title


class MapMilestone(Milestone, ClusterableModel):
    """A Milestone that belongs to a Map."""

    map = ParentalKey(Map, related_name="milestones")
    title = models.CharField(max_length=60, unique=True, verbose_name=_("Título"))
    latitude = LatitudeField(verbose_name="Latitud")
    longitude = LongitudeField(verbose_name="Longitud")
    place = models.TextField(verbose_name=_("Lugar"))
    pin_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("Icono del Pin"),
    )
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("map", widget=TextInput),
                FieldPanel("title"),
                FieldPanel("short_description"),
                FieldPanel("long_description"),
                FieldPanel("publish_date"),
                FieldRowPanel([FieldPanel("latitude"), FieldPanel("longitude")]),
                FieldPanel("place"),
                FieldPanel("image"),
                FieldPanel("pin_image"),
            ],
            heading=_("Estructura"),
        ),
        InlinePanel("resources", min_num=1, max_num=10, label=_("Recursos")),
    ]

    class Meta:
        """Define some custom properties for Timeline."""

        verbose_name = _("Hito de Mapa")
        verbose_name_plural = _("Hitos de Mapa")

    def __str__(self):
        """Return the string representation for MapMilestone."""
        return self.title


class MapMilestoneResource(Resource):
    """Intermediate model that relates a Resource to a Cloud."""

    milestone = ParentalKey(MapMilestone, related_name="resources")
