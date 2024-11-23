"""Define Timeline visualization for expositions app."""
from django.db import models
from django.forms import CheckboxInput, TextInput
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.blocks import (
    CharBlock,
    DateBlock,
    TextBlock,
    BooleanBlock,
    ListBlock,
    ChoiceBlock,
)
from wagtail.snippets.models import register_snippet
from wagtail.fields import StreamField

from expositions.edit_handlers import FixedObjectList, TimelineMilestoneInlineCreator
from expositions.models.resource import (
    Milestone,
    Resource,
    MilestoneComponent,
    ResourceComponent,
)


class TimelineMilestoneComponent(MilestoneComponent):
    """A Milestone that belongs to a Timeline."""

    title = CharBlock(max_length=60, label=_("Título"))
    start_date = DateBlock(
        label=_("Fecha Inicial"),
        help_text=_(
            "Fechas menores a 1950 se deben escribir manualmente usando el formato aaaa-mm-dd"
        ),
    )
    start_date_title = TextBlock(
        max_length=60, label=_("Titulo Fecha Inicial"), required=False
    )
    start_place = TextBlock(label=_("Lugar Inicial"), max_length=20, required=False)
    subtitle_1 = TextBlock(max_length=60, label=_("Subtítulo 1"), required=False)
    subtitle_2 = TextBlock(max_length=60, label=_("Subtítulo 2"), required=False)
    end_date = DateBlock(
        label=_("Fecha Final"),
        required=False,
        help_text=_(
            "Fechas menores a 1950 se deben escribir manualmente usando el formato aaaa-mm-dd"
        ),
    )
    end_date_title = TextBlock(
        max_length=60, label=_("Titulo Fecha Final"), required=False
    )
    end_place = TextBlock(label=_("Lugar Final"), max_length=20, required=False)
    category = ChoiceBlock(
        choices=[
            ("category_blue", _("Categoría 1 (Azul)")),
            ("category_magenta", _("Categoría 2 (Magenta)")),
            ("category_green", _("Categoría 3 (Verde)")),
            ("category_purple", _("Categoría 4 (Púrpura)")),
            ("category_yellow", _("Categoría 5 (Amarilla)")),
            ("category_red", _("Categoría 6 (Rojo)")),
        ],
        label="Categoría",
    )
    is_avatar = BooleanBlock(required=False, label=_("Es una Persona"))
    resources = ListBlock(ResourceComponent(), label=_("Recursos"))

    class Meta:
        label = _("Hito de Mapa")
        icon = "site"


@register_snippet
class Timeline(ClusterableModel):
    """Define an Timeline model."""

    title = models.CharField(max_length=150, unique=True, verbose_name=_("Título"))
    description = models.TextField(verbose_name=_("Descripción"))
    category_blue = models.TextField(
        max_length=255,
        verbose_name=_("Descripción Categoría Azul"),
        blank=True,
        null=True,
    )
    category_magenta = models.TextField(
        max_length=255,
        verbose_name=_("Descripción Categoría Magenta"),
        blank=True,
        null=True,
    )
    category_green = models.TextField(
        max_length=255,
        verbose_name=_("Descripción Categoría Verde"),
        blank=True,
        null=True,
    )
    category_purple = models.TextField(
        max_length=255,
        verbose_name=_("Descripción Categoría Púrpura"),
        blank=True,
        null=True,
    )
    category_yellow = models.TextField(
        max_length=255,
        verbose_name=_("Descripción Categoría Amarilla"),
        blank=True,
        null=True,
    )
    category_red = models.TextField(
        max_length=255,
        verbose_name=_("Descripción Categoría Roja"),
        blank=True,
        null=True,
    )

    milestones_content = StreamField(
        verbose_name="Hitos de lineas de tiempo",
        block_types=[("time_line_milestone", TimelineMilestoneComponent())],
        default=list,
        use_json_field=True
    )

    custom_panels = [
        MultiFieldPanel(
            [FieldPanel("title"), FieldPanel("description")], heading=_("Estructura")
        ),
        MultiFieldPanel(
            [
                FieldPanel("category_blue"),
                FieldPanel("category_magenta"),
                FieldPanel("category_green"),
                FieldPanel("category_purple"),
                FieldPanel("category_yellow"),
                FieldPanel("category_red"),
            ],
            heading=_("Categorías"),
        ),
        FieldPanel("milestones_content"),
    ]
    edit_handler = FixedObjectList(custom_panels, hide_on_add=("milestones",))

    def __str__(self):
        """Return the Timeline's name."""
        return self.title

    class Meta:
        """Define some custom properties for Timeline."""

        verbose_name = _("Linea de Tiempo")
        verbose_name_plural = _("Lineas de Tiempo")

    @property
    def categories(self):
        """Generate a Timeline's categories dict for json parsing."""
        categories = {
            "category_blue": self.category_blue,
            "category_magenta": self.category_magenta,
            "category_green": self.category_green,
            "category_purple": self.category_purple,
            "category_yellow": self.category_yellow,
            "category_red": self.category_red,
        }
        return {
            category: description
            for category, description in categories.items()
            if description is not None and description != ""
        }

    @property
    def categories_script_id(self):
        """Generate a categories script id for json parsign."""
        return f"timeline_categories_{self.pk}"

    @property
    def milestones_dict_list(self):
        """Generate a Milestones dict for json parsing."""
        milestones_list = []
        milestones_blocks = sorted(
            [block for block in self.milestones_content],
            key=lambda x: x.value["start_date"],
        )
        for index, milestone in enumerate(milestones_blocks):
            milestone_dict = {
                field: str(value)
                for field, value in milestone.value.items()
                if value is not None
            }
            milestone_dict["id"] = milestone.id

            milestone_dict["group_order"] = index
            milestones_list.append(milestone_dict)
        return milestones_list

    @property
    def milestones_script_id(self):
        """Generate a categories script id for json parsign."""
        return f"timeline_milestones_{self.pk}"


class TimelineMilestone(Milestone, ClusterableModel):
    """A Milestone that belongs to a Timeline."""

    timeline = ParentalKey(Timeline, related_name="milestones")
    title = models.CharField(max_length=60, unique=True, verbose_name=_("Título"))
    start_date = models.DateField(
        verbose_name=_("Fecha Inicial"),
        help_text=_(
            "Fechas menores a 1950 se deben escribir manualmente usando el formato aaaa-mm-dd"
        ),
    )
    start_date_title = models.TextField(
        max_length=60, verbose_name=_("Titulo Fecha Inicial"), blank=True, null=True
    )
    start_place = models.TextField(
        verbose_name=_("Lugar Inicial"), max_length=20, blank=True, null=True
    )
    subtitle_1 = models.TextField(
        max_length=60, verbose_name=_("Subtítulo 1"), blank=True, null=True
    )
    subtitle_2 = models.TextField(
        max_length=60, verbose_name=_("Subtítulo 2"), blank=True, null=True
    )
    end_date = models.DateField(
        verbose_name=_("Fecha Final"),
        blank=True,
        null=True,
        help_text=_(
            "Fechas menores a 1950 se deben escribir manualmente usando el formato aaaa-mm-dd"
        ),
    )
    end_date_title = models.TextField(
        max_length=60, verbose_name=_("Titulo Fecha Final"), blank=True, null=True
    )
    end_place = models.TextField(
        verbose_name=_("Lugar Final"), max_length=20, blank=True, null=True
    )
    category = models.CharField(
        max_length=16,
        choices=(
            ("category_blue", _("Categoría 1 (Azul)")),
            ("category_magenta", _("Categoría 2 (Magenta)")),
            ("category_green", _("Categoría 3 (Verde)")),
            ("category_purple", _("Categoría 4 (Púrpura)")),
            ("category_yellow", _("Categoría 5 (Amarilla)")),
            ("category_red", _("Categoría 6 (Rojo)")),
        ),
        verbose_name=_("Categoría"),
    )
    is_avatar = models.BooleanField(
        blank=True, default=False, verbose_name=_("Es una Persona")
    )
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("timeline", widget=TextInput),
                FieldPanel("title"),
                FieldRowPanel([FieldPanel("subtitle_1"), FieldPanel("subtitle_2")]),
                FieldPanel("short_description"),
                FieldPanel("long_description"),
                FieldRowPanel(
                    [
                        FieldPanel("start_date"),
                        FieldPanel("start_date_title"),
                        FieldPanel("start_place"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("end_date"),
                        FieldPanel("end_date_title"),
                        FieldPanel("end_place"),
                    ]
                ),
                FieldPanel("category"),
                FieldPanel("image"),
                FieldPanel("is_avatar", widget=CheckboxInput),
            ],
            heading=_("Estructura"),
        ),
        InlinePanel("resources", min_num=1, max_num=10, label=_("Recursos")),
    ]

    class Meta:
        """Define some custom properties for Timeline."""

        verbose_name = _("Hito de Linea de Tiempo")
        verbose_name_plural = _("Hitos de Linea de Tiempo")
        ordering = ["start_date"]

    def __str__(self):
        """Return the string representation for MapMilestone."""
        return self.title


class TimeLineMilestoneResource(Resource):
    """Intermediate model that relates a Resource to a Timeline Milestone."""

    milestone = ParentalKey(TimelineMilestone, related_name="resources")
