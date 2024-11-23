"""Define models that related to Equivalence for Harvester app."""

import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet

from resources.fields import IntegerCachedField
from resources.managers import SelectRelatedManager
from resources.models import TimestampModel

from ..managers import CreatorEquivalenceManager, SubjectEquivalenceManager
from .helpers import FIELDS_EQUIVALENCES_CHOICES, LONG_TEXT, SHORT_TEXT, TINY_TEXT


class Equivalence(TimestampModel):
    """List of equivalences for items such Languages and Types."""

    ICON_CHOICES = [
        ("3d", _("3d")),
        ("article", _("artículo")),
        ("audio", _("audio")),
        ("book", _("libro")),
        ("brochure", _("programa de mano (folleto)")),
        ("bulletin", _("boletin")),
        ("data", _("dato")),
        ("guide", _("guía de estudio")),
        ("interactive", _("interactivo")),
        ("map", _("mapa")),
        ("music-sheet", _("partitura")),
        ("newspaper", _("prensa")),
        ("objects", _("objeto físico")),
        ("picture", _("imágen")),
        ("series", _("serie monográfica")),
        ("software", _("software")),
        ("texts", _("texto")),
        ("thesis", _("tesis")),
        ("video", _("video")),
    ]

    name = models.CharField(max_length=SHORT_TEXT, verbose_name=_("nombre"))
    field = models.CharField(
        choices=FIELDS_EQUIVALENCES_CHOICES,
        max_length=SHORT_TEXT,
        verbose_name=_("campo"),
    )
    cite_type = models.CharField(
        choices=(
            ("standard", _("Estándar")),
            ("periodical", _("Publicación periódica")),
        ),
        max_length=SHORT_TEXT,
        null=True,
        blank=True,
        verbose_name=_("tipo de citación"),
        help_text=_("Especifica el tipo de citación a usar."),
    )
    full_date = models.BooleanField(
        null=True,
        blank=True,
        verbose_name=_("fecha completa"),
        help_text=_(
            "Especifica si se debe imprimir la fecha completa para recursos de este"
            " tipo. Si no se marca esta casilla se imprime sólo el año."
        ),
    )
    icon_class = models.CharField(
        max_length=TINY_TEXT,
        verbose_name=_("clase de íconos"),
        choices=ICON_CHOICES,
        null=True,
        blank=True,
        help_text=_(
            "Especifica el ícono a usar para los Recursos con equivalencia a este tipo"
            " de contenido. Sólo válido para `tipo de contenido`"
        ),
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name=_("prioridad"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text=_(
            "Especifica la prioridad de esta equivalencia. Números menores se muestran"
            " primero en los listados y filtros. Elementos sin prioridad se muestran"
            " de últimos."
        ),
    )

    wikidata_identifier = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Identificador Wikidata"),
        max_length=TINY_TEXT,
    )
    id_bne = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Identificador BNE"),
        max_length=TINY_TEXT,
    )
    id_unesco = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Identificador UNESCO"),
        max_length=TINY_TEXT,
    )
    id_lcsh = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Identificador LCSH"),
        max_length=TINY_TEXT,
    )
    id_lembp = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Identificador LEMBP"),
        max_length=TINY_TEXT,
    )

    class Meta(TimestampModel.Meta):
        """Define options for Equivalence."""

        verbose_name = _("equivalencia")
        verbose_name_plural = _("equivalencias")
        constraints = [
            models.UniqueConstraint(fields=["name", "field"], name="unique_equivalence")
        ]
        ordering = ["name", "priority"] + TimestampModel.Meta.ordering

    def __str__(self):
        """Return a string representation of a Equivalence."""
        return f"{self.name} [{self.get_field_display()}]"

    def clean(self):
        """
        Extend validation with custom field rules.

        - `icon_class` is only set for `type` fields
        - `full_date` is mandatory for `type` fields
        - `full_date` is only set for `type` fields
        - `cite_type` is mandatory for `type` fields
        - `cite_type` is only set for `type` fields

        """
        super().clean()

        errors = {}

        if self.field != "type":
            if self.icon_class:
                errors["icon_class"] = _(
                    "Los íconos sólo están disponibles para el campo"
                    " 'tipo de contenido'."
                )

            if self.full_date is not None:
                errors["full_date"] = _(
                    "La opción de fecha sólo está disponibles para el campo"
                    " 'tipo de contenido'."
                )

            if self.cite_type is not None:
                errors["cite_type"] = _(
                    "La opción de tipo de cita sólo está disponibles para el campo"
                    " 'tipo de contenido'."
                )

        else:
            if self.full_date is None:
                errors["full_date"] = _(
                    "La opción de fecha es obligatoria para equivalencias de campo"
                    " 'tipo de contenido'."
                )
            if self.cite_type is None:
                errors["cite_type"] = _(
                    "La opción de tipo de cita es obligatoria para equivalencias de"
                    " campo 'tipo de contenido'."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def search_url(self):
        """Return the search URL filtering by this content type."""
        search_url = reverse("search")
        search_field = "content_type" if self.field == "type" else self.field
        return f"{search_url}?{search_field}={self.id}"


class ContentResourceEquivalence(TimestampModel):
    """Map original values of resources to equivalences."""

    DEFAULT_MAPPING = _("Otros")

    equivalence = models.ForeignKey(
        Equivalence,
        on_delete=models.SET_NULL,
        verbose_name=_("equivalencia"),
        null=True,
        blank=True,
    )
    original_value = models.CharField(
        max_length=LONG_TEXT, verbose_name=_("valor original")
    )
    field = models.CharField(
        choices=FIELDS_EQUIVALENCES_CHOICES,
        max_length=SHORT_TEXT,
        verbose_name=_("campo"),
    )
    resources_count = IntegerCachedField(
        null=True, verbose_name=_("Número de recursos")
    )

    def update_cached_resources_count(self):
        """Update the Cached Resource Count Field and set an expiration."""
        self.resources_count = getattr(
            self, f"{self.field}equivalencerelation_set"
        ).count()
        self.resources_count_expiration = timezone.now() + datetime.timedelta(days=15)
        self.resources_count_expired = False

    objects = SelectRelatedManager(select_related=["equivalence"])

    class Meta(TimestampModel.Meta):
        """Define options for ContentResourceEquivalence."""

        verbose_name = _("equivalencia de recurso de contenido")
        verbose_name_plural = _("equivalencias de recurso de contenido")
        constraints = [
            models.UniqueConstraint(
                fields=["original_value", "field"], name="unique_mapping"
            )
        ]

    def __str__(self):
        """Return a string representation of a Equivalence."""
        equivalence = self.equivalence or _(" - sin mapeo - ")
        return f"{self.original_value} [{equivalence}]"

    def clean(self):
        """Validate that the mapping is a valid."""
        super().clean()

        if self.equivalence and self.equivalence.field != self.field:
            raise ValidationError(
                _("La equivalencia no es válida para el campo seleccionado.")
            )


class EquivalenceRelation(models.Model):
    """Abstract intermediate relation between equivalence and ContentResource."""

    contentresource = models.ForeignKey("ContentResource", on_delete=models.CASCADE)
    position = models.SmallIntegerField()
    to_delete = models.BooleanField(
        verbose_name=_("Borrado programado"), null=True, default=False
    )

    class Meta:
        """Define some custom properties for EquivalenceRelation."""

        abstract = True
        ordering = ["position"]
        unique_together = ["contentresource", "position"]


class LanguageEquivalenceRelation(EquivalenceRelation):
    """Intermediate relation for languages."""

    contentresourceequivalence = models.ForeignKey(
        ContentResourceEquivalence,
        on_delete=models.CASCADE,
        limit_choices_to={"field": "language"},
    )


class TypeEquivalenceRelation(EquivalenceRelation):
    """Intermediate relation for type."""

    contentresourceequivalence = models.ForeignKey(
        ContentResourceEquivalence,
        on_delete=models.CASCADE,
        limit_choices_to={"field": "type"},
    )


class SubjectEquivalence(Equivalence):
    """Proxy Model for separated Subject Equivalences"""

    objects = SubjectEquivalenceManager()

    class Meta:
        proxy = True
        verbose_name = _("Tema")
        verbose_name_plural = _("Temas")


class SubjectEquivalenceRelation(EquivalenceRelation):
    """Intermediate relation for subject."""

    contentresourceequivalence = models.ForeignKey(
        ContentResourceEquivalence,
        on_delete=models.CASCADE,
        limit_choices_to={"field": "subject"},
    )


class RightsEquivalenceRelation(EquivalenceRelation):
    """Intermediate relation for rights."""

    contentresourceequivalence = models.ForeignKey(
        ContentResourceEquivalence,
        on_delete=models.CASCADE,
        limit_choices_to={"field": "rights"},
    )


class CreatorEquivalence(Equivalence):
    """Proxy Model for separated Creator Equivalences"""

    objects = CreatorEquivalenceManager()

    class Meta:
        proxy = True
        verbose_name = _("Autor")
        verbose_name_plural = _("Autores")


class CreatorEquivalenceRelation(EquivalenceRelation):
    """Intermediate relation for creators."""

    contentresourceequivalence = models.ForeignKey(
        ContentResourceEquivalence,
        on_delete=models.CASCADE,
        limit_choices_to={"field": "creator"},
    )
