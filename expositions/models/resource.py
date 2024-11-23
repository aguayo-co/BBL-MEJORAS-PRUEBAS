"""Define Common visualizations for expositions app."""
import inspect
from collections import namedtuple

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from expositions.blocks import ResourceChooserBlock, TypeEquivalenceChooserBlock
from modelcluster.models import ClusterableModel
from wagtail.blocks import (
    CharBlock,
    TextBlock,
    RichTextBlock,
    DateBlock,
    StructBlock,
)
from wagtail.images.blocks import ImageChooserBlock

from resources.wagtail.edit_handlers import CollapsibleMultiFieldPanel
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField

LONG_DESCRIPTION_EDITOR_FEATURES = [
    "h3",
    "h4",
    "bold",
    "italic",
    "ol",
    "ul",
    "hr",
    "link",
    "superscript",
    "subscript",
    "blockquote",
]


class Resource(ClusterableModel):
    """Define a Resource that belongs to a Clusterable Model."""

    resource = models.ForeignKey(
        "harvester.ContentResource",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Recurso"),
        limit_choices_to={"visible": True, "setandresource__isnull": False},
    )
    title = models.TextField(blank=True, null=True, verbose_name=_("Título"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Descripción"))
    creator = models.TextField(blank=True, null=True, verbose_name=_("Autor"))
    date = models.DateField(blank=True, null=True, verbose_name=_("Fecha"))
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("Imagen"),
    )
    type = models.ForeignKey(
        "harvester.Equivalence",
        on_delete=models.SET_NULL,
        limit_choices_to={"field": "type"},
        null=True,
        blank=True,
        verbose_name=_("Tipo"),
    )

    panels = [
        FieldPanel("resource"),
        FieldPanel("image"),
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

    _processed_data = None

    @property
    def processed_data(self):
        """Expose the Resource Processor to the Exposition Scope."""
        if self._processed_data is not None:
            return self._processed_data

        overwritten_fields = [
            "title",
            "description",
            "creator",
            "date",
            "image",
            "type",
        ]

        ProcessedData = namedtuple(
            "ProcessedData",
            set(
                self.resource.processed_data._fields
                + tuple(
                    [
                        field
                        for field in overwritten_fields
                        if getattr(self, field, None) is not None
                        and getattr(self, field, "") != ""
                    ]
                )
            ),
        )

        ProcessedData.__getattr__ = self.resource.processed_data.__getattr__

        # Pass Methods
        for method_name, method in inspect.getmembers(
            self.resource.processed_data, predicate=inspect.ismethod
        ):
            if not method_name.startswith("__"):
                setattr(ProcessedData, method_name, method)

        old_fields = {
            old_field: getattr(self.resource.processed_data, old_field, None)
            for old_field in self.resource.processed_data._fields
        }
        new_fields = {
            field: getattr(self, field)
            for field in overwritten_fields
            if getattr(self, field) is not None and getattr(self, field, "") != ""
        }
        self._processed_data = ProcessedData(**{**old_fields, **new_fields})

        return self._processed_data

    def __str__(self):
        """Return the Resource's name."""
        return self.resource.__str__()


class Milestone(models.Model):
    """Base model for Milestones that contains Resources."""

    title = models.CharField(max_length=255, unique=True, verbose_name=_("Título"))
    short_description = models.TextField(
        max_length=300, verbose_name=_("Descripción Corta")
    )
    long_description = RichTextField(
        features=LONG_DESCRIPTION_EDITOR_FEATURES, verbose_name=_("Descripción Larga")
    )
    publish_date = models.DateField(
        blank=True, null=True, verbose_name=_("Fecha de Publicación")
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("Imagen"),
    )

    class Meta:
        """Define some custom properties for Milestone."""

        abstract = True
        verbose_name = _("Hito")
        verbose_name_plural = _("Hitos")


class ResourceComponent(StructBlock):
    """Define a Resource that belongs to a Clusterable Model."""

    resource = ResourceChooserBlock()
    title = TextBlock(required=False, label=_("Título"))
    description = TextBlock(required=False, label=_("Descripción"))
    creator = TextBlock(required=False, label=_("Autor"))
    date = DateBlock(required=False, label=_("Fecha"))
    image = ImageChooserBlock(
        required=False,
        label=_("Imagen"),
    )

    type = TypeEquivalenceChooserBlock()

    def to_python(self, value):
        """Expose the Resource Processor to the Exposition Scope."""
        values = super().to_python(value)

        overwritten_fields = [
            "title",
            "description",
            "creator",
            "date",
            "image",
            "type",
        ]

        ProcessedData = namedtuple(
            "ProcessedData",
            set(
                values["resource"].processed_data._fields
                + tuple(
                    [
                        field
                        for field in overwritten_fields
                        if values.get(field, None) is not None
                        and values.get(field, "") != ""
                    ]
                )
            ),
        )

        ProcessedData.__getattr__ = values["resource"].processed_data.__getattr__

        # Pass Methods
        for method_name, method in inspect.getmembers(
            values["resource"].processed_data, predicate=inspect.ismethod
        ):
            if not method_name.startswith("__"):
                setattr(ProcessedData, method_name, method)

        old_fields = {
            old_field: getattr(values["resource"].processed_data, old_field, None)
            for old_field in values["resource"].processed_data._fields
        }
        new_fields = {
            field: values.get(field)
            for field in overwritten_fields
            if values.get(field) is not None and values.get(field, "") != ""
        }
        if "type" in new_fields:
            new_fields["type"] = new_fields["type"].name
        values.update({"processed_data": ProcessedData(**{**old_fields, **new_fields})})

        return values


class MilestoneComponent(StructBlock):
    """Base block for Milestones that contains Resources."""

    title = CharBlock(max_length=255, label=_("Título"))
    short_description = TextBlock(max_length=300, label=_("Descripción Corta"))
    long_description = RichTextBlock(
        features=LONG_DESCRIPTION_EDITOR_FEATURES, label=_("Descripción Larga")
    )
    publish_date = DateBlock(required=False, label=_("Fecha de Publicación"))
    image = ImageChooserBlock(
        required=False,
        label=_("Imagen"),
    )

    class Meta:
        """Define some custom properties for Milestone."""

        label = _("Hito")
        icon = "list-ul"
