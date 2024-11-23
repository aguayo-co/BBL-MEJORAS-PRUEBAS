"""
Models definitions for Harvester App.

All models MUST inherit TimestampModel that contains control fields for creation-update.
"""

import datetime
import os
import random
import pymarc
import csv
import io
from lxml import etree
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    URLValidator,
)
from django.db import models
from django.db.models import OneToOneRel, JSONField
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from gm2m import GM2MField
from simple_history.models import HistoricalRecords
from sickle import Sickle
from sickle.iterator import OAIResponseIterator
from sickle.models import Record
from sickle.oaiexceptions import NoRecordsMatch

from resources.fields import IntegerCachedField, JSONCachedField, WysiwygField
from resources.managers import SelectRelatedManager
from resources.models import TimestampModel, ValidateFileMixin
from resources.validators import FileSizeValidator

from ..managers import (
    CollaborativeCollectionManager,
    CollectionQueryset,
    PromotedContentResourceManager,
    SetQueryset,
)
from .content_resource import ContentResource
from .equivalences import ContentResourceEquivalence
from .helpers import LONG_TEXT, SHORT_TEXT

bbl_logger = logging.getLogger("biblored")
User = get_user_model()  # pylint: disable=invalid-name


class AdminNotification(TimestampModel):
    """Admin notifications."""

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("tipo contenido")
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    notification_object_model = None
    notification_object_instance = None

    class Meta(TimestampModel.Meta):
        """Define properties for DataSource."""

        verbose_name = _("administrador de notificación")
        verbose_name_plural = _("administrador de notificaciones")

    def __str__(self):
        """Representación en string de las instancias del modelo."""
        return f"{self.created_at} -{self.object_id} - {self.content_type}"

    def get_notification_object_field(self, field_name):
        if hasattr(self.content_object, field_name):
            try:
                field_type = self.content_type._meta.get_field(
                    field_name
                ).get_internal_type()
                if field_type == "BooleanField":
                    return "Si" if getattr(self.content_object, field_name) else "No"
                else:
                    return getattr(self.content_object, field_name)
            except FieldDoesNotExist:
                return getattr(self.content_object, field_name)

        return None


class DataSource(ValidateFileMixin, TimestampModel):
    """Class for each Data Source to be Collected in Harvesting Process."""

    HARVEST_METHODS = (
        ("csv", _("cargar CSV")),
        ("ftp", _("descargar archivo desde FTP")),
        ("url", _("descargar archivo desde URL")),
        ("api", _("API de datos OAI")),
    )
    name = models.CharField(
        verbose_name=_("nombre"), max_length=SHORT_TEXT, unique=True
    )
    logo = models.ImageField(
        verbose_name=_("logo"),
        max_length=LONG_TEXT,
        null=True,
        blank=True,
        upload_to="datasources/logos/",
        validators=[
            FileSizeValidator(1000000),
            FileExtensionValidator(["jpg", "jpeg", "png"]),
        ],
    )
    image = models.ImageField(
        verbose_name=_("imagen"),
        max_length=LONG_TEXT,
        null=True,
        blank=True,
        upload_to="datasources/images/",
        validators=[
            FileSizeValidator(1000000),
            FileExtensionValidator(["jpg", "jpeg", "png"]),
        ],
    )
    config = JSONField(verbose_name=_("configuración"), default=dict)
    dynamic_image = JSONField(verbose_name=_("Imagen con URL Dinámica"), default=dict)
    data_mapping = JSONField(verbose_name=_("mapeo de datos"), null=True, blank=True)
    relevance = models.IntegerField(
        verbose_name=_("relevancia"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_(
            "La relevancia de la fuente afecta el orden de los Recursos en algunos"
            " listados. Números menores aparecen de primero en los listados."
        ),
    )
    exclusive = models.BooleanField(
        verbose_name=_("Exclusivo"),
        default=False,
        help_text=_(
            "Marca una fuente como de acceso exclusivo de MegaRed. Los"
            " contenidos de fuentes exclusivas son accesible sólo por usuarios"
            " autenticados en MegaRed."
        ),
    )
    online_resources = models.BooleanField(
        verbose_name=_("acceso digital"),
        default=False,
        help_text=_("Marca los contenidos de la fuente como de acceso digital."),
    )
    parking = models.BooleanField(
        verbose_name=_("parqueadero"),
        default=False,
        help_text=_("Información de parqueadero para el público en la fuente."),
    )
    address = models.TextField(
        max_length=LONG_TEXT,
        blank=True,
        verbose_name=_("dirección"),
        help_text=_("Dirección física de la fuente para acceso del público."),
    )
    contact = models.CharField(
        max_length=SHORT_TEXT,
        blank=True,
        verbose_name=_("contacto"),
        help_text=_("Información de contacto de la fuente."),
    )
    is_ally = models.BooleanField(
        verbose_name=_("aliado"),
        default=False,
        help_text=_(
            "Marca la fuente como 'aliado'. Un aliado tiene mención especial "
            "en el sitio."
        ),
    )

    class Meta(TimestampModel.Meta):
        """Define properties for DataSource."""

        verbose_name = _("fuente de datos")
        verbose_name_plural = _("fuentes de datos")
        permissions = [
            ("can_harvest", "Puede cosechar"),
            (
                "can_reindex_datasource",
                (
                    "Puede marcar todos los recursos de esta fuente de datos "
                    "para reindexar"
                ),
            ),
        ]

    def __str__(self):
        """Return a string representation of a Data Source."""
        return self.name

    def clean(self):
        """Validate required data for ally."""
        super().clean()

        if self.is_ally and not self.logo:
            raise ValidationError(_("Para ser aliado se necesita un logo."))

    @property
    def search_url(self):
        """Return the search URL filtering by this DataSource type."""
        search_url = reverse("search")
        return f"{search_url}?data_sources={self.id}"

    def has_expired_dynamic_identifiers(self):
        """Check if related datasource has expired Dynamic Identifiers."""
        return self.contentresource_set.filter(
            ContentResource.get_cached_field_expired_filters("dynamic_identifier")
        ).exists()

    def save(self, **kwargs):
        """Overrides the save method to track changes in certain fields related to indexing."""
        from search_engine.functions.es_backend_helpers import (
            mark_resources_for_reindex,
        )

        # Fields to track changes
        fields_to_track = ["name", "relevance", "online_resources"]
        # Get current value
        try:
            current_instance = DataSource.objects.get(pk=self.pk)
            # Compare with new values
            mark_for_reindex = any(
                [
                    (
                        False
                        if getattr(current_instance, field) == getattr(self, field)
                        else True
                    )
                    for field in fields_to_track
                ]
            )

            # If any change is detected, reindex
            if mark_for_reindex:
                mark_resources_for_reindex(self.contentresource_set.all())
        except DataSource.DoesNotExist:
            # New instance, no need to reindex
            pass
        # Save
        super().save(**kwargs)


class Schedule(TimestampModel):
    """Handles the schedule of a Data Source."""

    DAYS_CHOICES = [
        (1, _("lunes")),
        (2, _("martes")),
        (3, _("miércoles")),
        (4, _("jueves")),
        (5, _("viernes")),
        (6, _("sábados")),
        (7, _("domingos")),
        (8, _("festivos")),
        (9, _("domingos y festivos")),
    ]

    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, verbose_name=_("fuente de datos")
    )
    day = models.IntegerField(choices=DAYS_CHOICES, null=False, verbose_name=_("día"))
    opening = models.TimeField(
        verbose_name=_("hora de apertura"), null=True, blank=True
    )
    closing = models.TimeField(verbose_name=_("hora de cierre"), null=True, blank=True)
    closed = models.BooleanField(verbose_name=_("cerrado"), default=False)

    class Meta(TimestampModel.Meta):
        """Define properties for Schedule."""

        verbose_name = _("horario")
        verbose_name_plural = _("horarios")
        constraints = [
            models.UniqueConstraint(
                fields=["data_source", "day"], name="unique_day_per_schedule"
            )
        ]
        ordering = ["day"] + TimestampModel.Meta.ordering

    def __str__(self):
        """Return schedule human readable info as string."""
        return _("Horario para días %(day)s") % {"day": self.day}


class DynamicIdentifierConfig(TimestampModel):
    """
    Configuration to build a dynamic identifier.

    Each configuration should indicate a `field` from where to get the data,
    and a `capture_expression`, which is a regular expression whose capture groups
    will be used to extract data from the field.
    """

    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, verbose_name=_("fuente de datos")
    )
    field = models.TextField(verbose_name=_("Campo Dublin Core"))
    capture_expression = models.TextField(verbose_name=_("Expresión de Captura"))

    class Meta(TimestampModel.Meta):
        """Define properties for Dynamic Identifier Config."""

        verbose_name = _("Configuración de Identificador Dinámico")
        verbose_name_plural = _("Configuración de Identificadores Dinámicos")

    def __str__(self):
        """Return a string representation of a Dynamic Identifier Config."""
        return f"{self.field} - {self.capture_expression}"


class CollectionsGroup(TimestampModel):
    """Group of Collections."""

    title = models.CharField(
        verbose_name=_("nombre para el grupo de colecciones"),
        max_length=100,
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("dueño"))
    collections = GM2MField(
        through="CollectionsGroupCollection", verbose_name=_("colecciones")
    )
    collections_count = IntegerCachedField(
        null=True, verbose_name=_("número de colecciones")
    )

    class Meta(TimestampModel.Meta):
        """Define properties for Collection."""

        verbose_name = _("grupo de colecciones")
        verbose_name_plural = _("grupos de colecciones")
        constraints = [
            models.UniqueConstraint(
                fields=["title", "owner"], name="unique title - owner combination"
            )
        ]

    def __str__(self):
        """Return a string representation of a Collections Group."""
        return self.title

    def update_cached_collections_count(self):
        """Update the Cached Resource Count Field and set an expiration."""
        # pylint: disable=attribute-defined-outside-init
        self.collections_count = self.collections.all().count()
        self.collections_count_expiration = timezone.now() + datetime.timedelta(days=15)
        self.collections_count_expired = False
        # pylint: enable=attribute-defined-outside-init

    def get_absolute_url(self):
        """Return url for current instance."""
        return reverse("collectionsgroup", args=[self.pk])


class CollectionsGroupCollection(TimestampModel):
    """Generic many to many relation between collections groups and collections."""

    collections_group = models.ForeignKey(
        CollectionsGroup,
        on_delete=models.CASCADE,
    )
    content_type = models.ForeignKey(
        ContentType,
        related_name="content_type_set_for_%(class)s",
        on_delete=models.CASCADE,
    )
    object_pk = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")

    class Meta:
        """Define some custom properties for CollectionsGroupCollection."""

        indexes = TimestampModel._meta.indexes + [
            models.Index(fields=["object_pk"]),
            models.Index(fields=["content_type"]),
        ]

    def __str__(self):
        return f"collections_group: {self.collections_group}, content_type:  {self.content_type}, object_pk:  {self.object_pk}"  # noqa: E501

    @classmethod
    def update_collection_groups(
        cls,
        collection,
        collections_groups,
        clear=True,
        initial_collections_group=None,
        user=None,
    ):
        if clear and (initial_collections_group or user):
            if not initial_collections_group:
                initial_collections_group = list(
                    collection.collections_groups.select_related("collections_group")
                    .filter(collections_group__owner=user)
                    .all()
                    .values_list("collections_group", flat=True)
                )

            cls.objects.filter(
                content_type=ContentType.objects.get_for_model(collection.__class__),
                object_pk=collection.pk,
                collections_group__in=initial_collections_group,
            ).delete()
        new_objects_list = []
        for collection_group in collections_groups:
            new_objects_list.append(
                cls(collections_group=collection_group, content_object=collection)
            )
        return cls.objects.bulk_create(new_objects_list)

    @classmethod
    def add_to_favorites(cls, collection, user):
        favorite_group = CollectionsGroup.objects.get(title="favoritos", owner=user)
        result = cls.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(collection.__class__),
            object_pk=collection.pk,
            collections_group=favorite_group,
        )
        return result

    @classmethod
    def remove_from_favorites(cls, collection, user):
        favorite_group = CollectionsGroup.objects.get(title="favoritos", owner=user)
        result = cls.objects.filter(
            content_type=ContentType.objects.get_for_model(collection.__class__),
            object_pk=collection.pk,
            collections_group=favorite_group,
        ).delete()
        return result


class Set(ValidateFileMixin, TimestampModel):
    """A set is a collection of content resources that were or will be harvested."""

    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, verbose_name=_("fuente de datos")
    )
    name = models.CharField(verbose_name=_("nombre del set"), max_length=SHORT_TEXT)
    spec = models.CharField(verbose_name=_("especificación"), max_length=SHORT_TEXT)
    image = models.ImageField(
        verbose_name=_("foto de portada"),
        max_length=LONG_TEXT,
        null=True,
        blank=True,
        upload_to="sets/images/",
        validators=[
            FileSizeValidator(1000000),
            FileExtensionValidator(["jpg", "jpeg", "png"]),
        ],
    )
    description = WysiwygField(blank=True, default="", verbose_name="descripción")
    visible = models.BooleanField(
        default=True,
        help_text=_(
            "Permite mostrar u ocultar un Set y todos los Recursos de contenido"
            " asociados a este en el sitio. Un Recurso es visible cuando al menos uno"
            " de los Sets a los que pertenece es visible."
        ),
    )
    home_site = models.BooleanField(
        verbose_name=_("Home principal"),
        default=False,
        help_text=_("Muestra el Set en el home principal del sitio."),
    )
    home_internal = models.BooleanField(
        verbose_name=_("Home interno"),
        default=False,
        help_text=_("Destaca el Set en el home interno o listado de Sets."),
    )
    resources_count = IntegerCachedField(
        null=True, verbose_name=_("Número de recursos")
    )
    data_source_url = models.TextField(
        verbose_name=_("Enlace externo de la fuente"),
        validators=[URLValidator()],
        blank=True,
    )

    resources_by_type_count = JSONCachedField(null=True)

    collections_groups = GenericRelation(
        CollectionsGroupCollection, object_id_field="object_pk", related_query_name="+"
    )

    objects = SetQueryset.as_manager()

    def update_cached_resources_count(self):
        """Update the Cached Resource Count Field and set an expiration."""
        self.resources_count = self.setandresource_set.count()
        # pylint: disable=attribute-defined-outside-init
        self.resources_count_expiration = timezone.now() + datetime.timedelta(days=15)
        self.resources_count_expired = False
        # pylint: enable=attribute-defined-outside-init

    class Meta(TimestampModel.Meta):
        """Define properties for Set."""

        verbose_name = "Colección institucional"
        verbose_name_plural = "Colecciones institucionales"
        indexes = TimestampModel.Meta.indexes + [models.Index(fields=["visible"])]
        constraints = [
            models.UniqueConstraint(
                fields=["spec", "data_source"], name="unique_spec_per_source"
            )
        ]

    def __str__(self):
        """Return a string representation of a Set."""
        return self.name

    def update_cached_resources_by_type_count(self):
        """Update the Cached Resource By Type Count Field and set an expiration."""

        counter = self.contentresource_set.visible().by_type__count()
        default_mapping = ContentResourceEquivalence.DEFAULT_MAPPING
        unmapped = None

        if default_mapping in counter:
            unmapped = counter.pop(default_mapping)

        by_type__count = {_type: counter[_type] for _type in list(counter)[:3]}

        if unmapped is not None or len(counter) > 3:
            by_type__count[default_mapping] = ""

        self.resources_by_type_count = {
            str(key): int(value) if value else 0
            for key, value in sorted(
                by_type__count.items(), key=lambda item: int(item[1]) if item[1] else 0
            )
        }
        # pylint: disable=attribute-defined-outside-init
        self.resources_by_type_count_expiration = timezone.now() + datetime.timedelta(
            days=15
        )
        self.resources_by_type_count_expired = False
        # pylint: enable=attribute-defined-outside-init

    def get_absolute_url(self):
        """Return url for current instance."""
        return reverse("set", args=[self.pk])


class Review(TimestampModel):
    """A review for a ContentResource."""

    resource = models.ForeignKey(
        ContentResource, on_delete=models.CASCADE, verbose_name=_("recurso")
    )
    title = models.CharField(
        verbose_name=_("título"), max_length=256, null=True, blank=False
    )
    text = models.TextField(
        verbose_name=_("reseña"),
        max_length=3000,
        validators=[
            MinLengthValidator(
                100,
                message=_(
                    "Asegúrate de que este valor tenga como mínimo "
                    "%(limit_value)s (este tiene %(show_value)s)."
                ),
            )
        ],
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("calificación"),
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("autor"))
    admin_notification = GenericRelation(AdminNotification)

    class Meta(TimestampModel.Meta):
        """Define properties for Review."""

        verbose_name = _("reseña")
        verbose_name_plural = _("reseñas")

    def __str__(self):
        """Return a string representation of a Review."""
        return _("%(rating)d - Review para: %(resource)s") % {
            "rating": self.rating,
            "resource": self.resource,
        }

    def get_absolute_url(self):
        """Return url for current instance."""
        return reverse("content_resource", args=[self.resource.pk])


class PromotedContentResource(ValidateFileMixin, TimestampModel):
    """Promote a content resource and add extra details."""

    RESOURCE_FILTERS = {"visible": True, "sets__visible": True}

    resource = models.OneToOneField(
        ContentResource,
        on_delete=models.CASCADE,
        primary_key=True,
        limit_choices_to=RESOURCE_FILTERS,
        verbose_name=_("recurso"),
    )
    priority = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name=_("prioridad"),
        help_text=_(
            "Especifica la prioridad de este Recurso. Números menores se muestran"
            " primero en los listados."
        ),
    )
    image = models.ImageField(
        verbose_name=_("imagen"),
        max_length=LONG_TEXT,
        upload_to="promoted_contentresources/images/",
        validators=[
            FileSizeValidator(1000000),
            FileExtensionValidator(["jpg", "jpeg", "png"]),
        ],
    )

    objects = PromotedContentResourceManager()

    class Meta(TimestampModel.Meta):
        """Define options for PromotedContentResource."""

        verbose_name = _("recurso de contenido promocionado")
        verbose_name_plural = _("recursos de contenido promocionado")
        ordering = ["priority"] + TimestampModel.Meta.ordering

    def __str__(self):
        """Return a string representation of a PromotedContentResource."""
        return _("Promovido: %(resource)s") % {"resource": self.resource}


class SetAndResource(TimestampModel):
    """Define association between Set and ContentResource."""

    resource = models.ForeignKey(
        ContentResource, on_delete=models.CASCADE, related_name="setandresource"
    )
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    harvest_task = models.CharField(null=False, max_length=200)

    class Meta(TimestampModel.Meta):
        """Define options for SetAndResource."""

        constraints = [
            models.UniqueConstraint(
                fields=["resource", "set"], name="unique_resource_per_set"
            )
        ]
        indexes = [
            models.Index(fields=["resource"]),
        ]


class Collection(ValidateFileMixin, TimestampModel):
    """A collection is an group of content resources that an user collect."""

    title = models.CharField(verbose_name=_("nombre para la colección"), max_length=100)
    description = models.TextField(verbose_name=_("descripción"), max_length=200)
    image = models.ImageField(
        verbose_name=_("foto de portada"),
        max_length=LONG_TEXT,
        null=True,
        blank=True,
        upload_to="collections/images/",
        validators=[
            FileSizeValidator(1000000),
            FileExtensionValidator(["jpg", "jpeg", "png"]),
        ],
    )
    resources = models.ManyToManyField(
        ContentResource, blank=True, through="CollectionAndResource"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("dueño"))
    public = models.BooleanField(
        verbose_name=_("Colección pública"),
        help_text=_(
            "Una colección pública es visible por todos los usuarios del portal."
            " Cuando no es pública, sólo el dueño la puede ver."
        ),
        default=True,
    )
    visible = models.BooleanField(
        default=True, help_text=_("Permite mostrar u ocultar la Colección en el sitio.")
    )
    home_site = models.BooleanField(
        verbose_name=_("Home principal"),
        default=False,
        help_text=_("Muestra la Colección en el home principal del sitio."),
    )
    home_internal = models.BooleanField(
        verbose_name=_("Home interno"),
        default=False,
        help_text=_(
            "Destaca la colección en el Home interno o listado de Colecciones."
        ),
    )
    detail_image = models.FilePathField(
        verbose_name=_("Imagen detalle de colección"),
        path=os.path.join(
            settings.BASE_DIR,
            "resources",
            "static",
            "biblored",
            "collections",
            "detail_images",
        ),
        null=True,
        match=r"\.(jpg|jpeg|png|svg)$",
    )
    default_cover_image = models.FilePathField(
        verbose_name=_("Imagen de portada por defecto"),
        path=os.path.join(
            settings.BASE_DIR,
            "resources",
            "static",
            "biblored",
            "collections",
            "cover_images",
        ),
        null=True,
        match=r"\.(jpg|jpeg|png|svg)$",
    )
    resources_count = IntegerCachedField(
        null=True, verbose_name=_("Número de recursos")
    )

    resources_by_type_count = JSONCachedField(null=True)
    collections_groups = GenericRelation(
        CollectionsGroupCollection, object_id_field="object_pk", related_query_name="+"
    )

    history = HistoricalRecords()

    objects = SelectRelatedManager.from_queryset(CollectionQueryset)(
        prefetch_related=["owner__profile", "owner__country"],
    )
    admin_notification = GenericRelation(AdminNotification)

    def update_cached_resources_count(self):
        """Update the Cached Resource Count Field and set an expiration."""
        # pylint: disable=attribute-defined-outside-init
        self.resources_count = self.resources.all().count()
        self.resources_count_expiration = timezone.now() + datetime.timedelta(days=15)
        self.resources_count_expired = False
        # pylint: enable=attribute-defined-outside-init

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """Save the current Collection and assign a random detail image if required."""
        non_static_path = os.path.join(settings.BASE_DIR, "resources", "static")
        all_images = {
            os.path.relpath(image_path, non_static_path)
            for image_path in dict(
                self._meta.get_field("detail_image").formfield().choices
            )
        }
        if not self.detail_image or self.detail_image not in all_images:
            cache_key = "collection_used_detail_images"
            used_images = cache.get(cache_key) or set()

            available_images = (
                list(all_images)
                if all_images == used_images
                else list(all_images - used_images)
            )

            self.detail_image = random.choice(available_images)
            used_images.add(self.detail_image)
            cache.set(cache_key, used_images)

        if not self.default_cover_image:
            self.default_cover_image = (
                self._meta.get_field("default_cover_image").formfield().choices[0][0]
            )

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta(TimestampModel.Meta):
        """Define properties for Collection."""

        verbose_name = _("colección")
        verbose_name_plural = _("colecciones")
        default_manager_name = "objects"
        indexes = TimestampModel.Meta.indexes + [
            models.Index(fields=["title"]),
            models.Index(fields=["visible"]),
        ]

    def __str__(self):
        """Return a string representation of a Collection."""
        return self.title

    def get_absolute_url(self):
        """Return url for current instance."""
        return reverse("collection", args=[self.pk])

    @property
    def resources_list(self):
        """Return associated resources."""
        return self.resources.visible()  # pylint: disable=no-member

    def update_cached_resources_by_type_count(self):
        """Update the Cached Resource By Type Count Field and set an expiration."""

        counter = self.resources.visible().by_type__count()
        default_mapping = ContentResourceEquivalence.DEFAULT_MAPPING
        unmapped = None

        if default_mapping in counter:
            unmapped = counter.pop(default_mapping)

        by_type__count = {_type: counter[_type] for _type in list(counter)[:3]}

        if unmapped is not None or len(counter) > 3:
            by_type__count[default_mapping] = ""

        self.resources_by_type_count = {
            str(key): int(value) if value else 0
            for key, value in sorted(
                by_type__count.items(), key=lambda item: int(item[1]) if item[1] else 0
            )
        }
        # pylint: disable=attribute-defined-outside-init
        self.resources_by_type_count_expiration = timezone.now() + datetime.timedelta(
            days=15
        )
        self.resources_by_type_count_expired = False
        # pylint: enable=attribute-defined-outside-init

    def get_subtype(self):
        """Return the subtype of this model, if it has one."""
        for field in self._meta.get_fields(include_hidden=True):
            if isinstance(field, OneToOneRel) and hasattr(self, field.name):
                return field.name

        return None

    @property
    def collection_group_exclude_favorites(self):
        """Retorna los grupos de colecciones omitiendo los favoritos."""
        return self.collections_groups.exclude(collections_group__title="favoritos")


class CollectionAndResource(TimestampModel):
    """Define association between Collection and ContentResource."""

    resource = models.ForeignKey(
        ContentResource,
        on_delete=models.CASCADE,
        related_name="collectionandresource",
        verbose_name=_("recurso"),
    )
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    class Meta(TimestampModel.Meta):
        """Define properties for CollectionAndResource."""

        verbose_name = _("recurso en colección")
        verbose_name_plural = _("recursos en colecciones")

    def __str__(self):
        """Return a string representation of a CollectionAndResource."""
        return f"Recurso: {self.resource_id} - Colección: {self.collection_id}"


class CollaborativeCollection(Collection):
    """Store a group of ContentResources that a User collects and share with others."""

    collaborators = models.ManyToManyField(
        User, verbose_name=_("colaboradores"), blank=True, through="Collaborator"
    )

    history = HistoricalRecords()

    objects = CollaborativeCollectionManager()

    @property
    def active_collaborators(self):
        return [
            user
            for user in self.collaborators_users
            if user.pk in self.active_collaborators_id
        ]

    @property
    def requested_collaborators(self):
        return [
            user
            for user in self.collaborators_users
            if user.pk in self.requested_collaborators_id
        ]

    @property
    def invited_collaborators(self):
        return [
            user
            for user in self.collaborators_users
            if user.pk in self.invited_collaborators_id
        ]

    @classmethod
    def create_from_collection(cls, collection):
        """Create a Collaborative Collection based on a Collection using same ids."""
        # Promote to CollaborativeCollection
        collection_relation_field = cls._meta.parents.get(Collection, None)
        collection_fields = {
            field.name: getattr(collection, field.name)
            for field in collection._meta.fields
        }
        collection_fields[collection_relation_field.name] = collection
        collaborative_collection = cls(**collection_fields)
        collaborative_collection.save()
        return collaborative_collection

    class Meta:
        """Define properties for a Collaborative Collection."""

        verbose_name = _("colección colaborativa")
        verbose_name_plural = _("colecciones colaborativas")
        base_manager_name = "objects"


class Collaborator(TimestampModel):
    """Users of a Collaborative Collection (Collaborator) and its invitation status."""

    INVITATION_AND_REQUEST_STATUS_CHOICES = [
        (-1, _("invitado")),
        (-2, _("solicitado")),
        (1, _("colaborando")),
    ]

    collaborativecollection = models.ForeignKey(
        CollaborativeCollection, on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("usuario"),
    )
    status = models.SmallIntegerField(
        choices=INVITATION_AND_REQUEST_STATUS_CHOICES,
        help_text=_(
            "Un usuario puede colaborar en una colección cuando su estado es "
            "'colaborando'"
        ),
        verbose_name=_("estado"),
    )

    class Meta(TimestampModel.Meta):
        """Define properties for Collaborator."""

        verbose_name = _("colaborador de la colección")
        verbose_name_plural = _("colaboradores de la colección")
        constraints = [
            models.UniqueConstraint(
                fields=["collaborativecollection", "user"], name="unique_collaborator"
            )
        ]

    def __str__(self):
        """Return a string representation of a Collaborative Collection Collaborator."""
        return f"{self.user.full_name}"


class SharedResource(TimestampModel):
    """Shared resources register."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    resource = models.ForeignKey(ContentResource, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(
        User,
        verbose_name=_("compartido con"),
        through="SharedResourceUser",
    )

    class Meta:
        unique_together = (
            "owner",
            "resource",
        )


class SharedResourceUser(TimestampModel):
    """Shared resources with."""

    SHARED_RESOURCE_STATUS_CHOICES = [
        (0, _("no leído")),
        (1, _("leído")),
        (2, _("ignorado")),
    ]

    shared_resource = models.ForeignKey(SharedResource, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.SmallIntegerField(
        choices=SHARED_RESOURCE_STATUS_CHOICES,
        default=SHARED_RESOURCE_STATUS_CHOICES[0][0],
    )

    def mark_as_read(self, user):
        """Mark shared resource notification as read."""
        if self.status == 0 and self.user == user:
            self.status = self.SHARED_RESOURCE_STATUS_CHOICES[1][0]
            return self.save()

    def __str__(self):
        return (
            f"fecha: {self.created_at} - "
            f"status: {self.SHARED_RESOURCE_STATUS_CHOICES[self.status][1]} - "
            f"compartido por: {self.shared_resource.owner.full_name}"
        )


class StageHarvest(models.Model):
    ''' Harvester's stages '''
    
    HARVEST_STAGE_CHOICES = [
        (0, _("Cosechamiento Creado")),
        (1, _("Cosechamiento Iniciado")),
        (2, _("Descargando archivo")),
        (3, _("Archivo descargado")),
        (4, _("Archivo no descargado")),
        (5, _("Archivo guardado")),
        (6, _("Indexado")),
        (7, _("Indexado en Curso")),
        (8, _("Finalizado")),
    ]

    stage = models.SmallIntegerField(
        verbose_name=_("Etapa"),
        choices=HARVEST_STAGE_CHOICES,
        default=HARVEST_STAGE_CHOICES[0][0],
    )
    harvest = models.ForeignKey(
        'harvester.Harvest',
        on_delete=models.CASCADE,
        verbose_name=_("Cosechamiento"),
    )
    start_date = models.DateTimeField(verbose_name=_("Fecha inicio"), auto_now_add=True)
    end_date = models.DateTimeField(verbose_name=_("Fecha fin"), auto_now_add=True)

    def __str__(self):
        return self.get_stage_display()

    class Meta:
        unique_together = ('stage', 'harvest')


class Harvest(models.Model):
    ''' Register a task of harvester '''
    
    HARVEST_STATUS_CHOICES = [
        (0, _("Iniciado")),
        (1, _("En curso")),
        (2, _("Completado con errores")),
        (3, _("Completado correctamente")),
    ]
    
    data_source_name = models.CharField(verbose_name=_("Fuente de datos"))
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario"),
    )
    group_id = models.CharField(verbose_name=_("Identicador de Tarea"))
    status = models.SmallIntegerField(
        verbose_name=_("Estado"),
        choices=HARVEST_STATUS_CHOICES,
        default=HARVEST_STATUS_CHOICES[0][0],
    )
    stage = models.ForeignKey(
        StageHarvest,
        on_delete=models.CASCADE,
        related_name='current_harvest_stage',
        verbose_name=_('Etapa actual'),
        blank=True,
        null=True
    )

    start_date = models.DateTimeField(verbose_name=_("Fecha inicio"), auto_now_add=True)
    end_date = models.DateTimeField(verbose_name=_("Fecha fin"), blank=True, null=True)
    remaining_time = models.CharField(
        verbose_name=_("Restante estimado"),
        blank=True,
        null=True,
        default='0 d, 0 h, 0 m, 0 s'
    )

    counter_resource = JSONField(verbose_name=_("Contador de recursos"), default=dict, null=True)
    progress_count = models.BigIntegerField(verbose_name=_("Recursos indexados"), default=0, blank=True, null=True)
    counter_total_resources = models.BigIntegerField(
        verbose_name=_("Recursos en total"),
        default=0,
        blank=True, null=True
    )

    def get_status_display(self):
        return dict(self.HARVEST_STATUS_CHOICES).get(self.status, 'Desconocido')
    get_status_display.short_description = "Estado"

    def get_data_source_name(self):
        return f'Cosechamiento {self.data_source_name}'
    get_data_source_name.short_description = "Fuente"

    def get_progress_count(self):
        return f'{self.progress_count} de {self.counter_total_resources}'
    get_progress_count.short_description = "Recursos Indexados"
    
    def __str__(self):
        """Return a string representation of a Harvest History."""
        return f'Historial de la fuente { self.data_source_name }'
    
    class Meta:
        verbose_name = _("Historial de Cosechamiento")
        verbose_name_plural = _("Historial de Cosechamientos")


class ControlHarvestStatus():

    def __init__(self, data_source=None, group_id=None, user=None, stage=None, status=None, results=None, a_set=None):
        self.data_source = data_source
        self.group_id = group_id
        self.user = user
        self.stage = stage
        self.status = status
        self.results = results
        self.progress = 0
        self.a_set = a_set

    def create_stage_first_time(self):
        # Create harvest instance
        harvest = Harvest(
            data_source_name=(
                f'Fuente {self.data_source.name} - Set {self.a_set[1]}' 
                if self.a_set
                else f'Fuente {self.data_source.name}'
            ),
            group_id=self.group_id,
            user=self.user,
            status=self.status
        )
        harvest.save()

        stage = StageHarvest.objects.create(
            stage=self.stage,
            harvest=harvest,
        )

        harvest.stage = stage
        harvest.save()

    def change_stage_by_step(self, is_indexing=False):
        ''' Change stage in the harvest process '''
        
        # Validar que exista el cosechamiento para que no entre la primera vez que carga el archivo
        harvest = Harvest.objects.filter(group_id=self.group_id).first()
        if harvest:
            self.average_harvest_time(harvest)

            # Para que el estado del cosechamiento quede en "con errores"
            if not harvest.status == 2:
                harvest.status = self.status
                harvest.save() # Para poder guardar la instancia de la Stage

                current_stage, created = StageHarvest.objects.get_or_create(
                    stage=self.stage,
                    harvest=harvest
                )
                
                harvest.stage = current_stage

                # Si esta en save_resources en la segunda vuelta entra a cambiar el estado del indexado
                if is_indexing:
                    harvest.progress_count = self.get_calculate_progress(harvest)

                    if not created:
                        self.stage = 7
                        next_stage, _ = StageHarvest.objects.get_or_create(
                            stage=self.stage,
                            harvest=harvest,
                        )

                        # Cambia etapa a indexado en curso
                        if next_stage:
                            harvest.stage = next_stage

            # Etapa finalizado o si se termino con errores
            stage_seven_exists = StageHarvest.objects.filter(harvest=harvest, stage=7).exists()
            if self.stage == 8 or self.stage == 1 and not stage_seven_exists or self.status == 2:
                harvest.end_date = datetime.datetime.now()
                harvest.counter_resource = self.results
                harvest.remaining_time = '0 d, 0 h, 0 m, 0 s'

            # Actualizar fecha final de la etapa anterior
            self.update_date_prev_stage(harvest, self.stage)

            harvest.save()
        
    def update_date_prev_stage(self, harvest, stage_id):
        ''' Update date of prev stage in a current harvest history '''

        # Si la etapa es indexado en curso se actualiza su misma fecha
        prev_stage_id = 7 if stage_id == 7 else stage_id - 1

        # Se salta la etapa archivo no descargado
        if stage_id == 5:
            prev_stage_id = 3

        if self.data_source:
            # Cuando no se descarga el archivo
            if not self.data_source.config['method'] == 'url':
                # De la etapa indexado devuelve a iniciado
                if stage_id == 6:
                    prev_stage_id = 1

        # Si no entro a la etapa indexado
        stage_seven_exists = StageHarvest.objects.filter(harvest=harvest, stage=7).exists()
        if stage_id == 8 and not stage_seven_exists:
            prev_stage_id = 1

        # Para el metodo OAI
        stage_zero_exists = StageHarvest.objects.filter(harvest=harvest, stage=0).exists()
        if stage_id == 1 and not stage_zero_exists:
            prev_stage_id = 1

        # Actualiza el objeto de la etapa anterior
        prev_stage = StageHarvest.objects.get(harvest=harvest, stage=prev_stage_id)
        prev_stage.end_date = datetime.datetime.now()
        harvest.end_date = datetime.datetime.now()
        prev_stage.save()

    def average_harvest_time(self, harvest):
        ''' Calculate average time from a current harvest with previously same harvesters '''
        if harvest.end_date:
            # Tiempo de diferencia cosechamiento actual en segundos
            current_difference_time = (
                harvest.end_date - harvest.start_date
            ).total_seconds()
            # Obtener fechas de cosechamientos anteriores correctos de la misma fuente
            harvesters_time = Harvest.objects.filter(
                data_source_name=harvest.data_source_name,
                status=3
            ).values('start_date', 'end_date')

            restant_time = None
            if harvesters_time:
                difference_times_list = []
                # Obtener total de segundos de cada cosechamiento
                for harvest_time in harvesters_time:
                    difference_time = (
                        harvest_time['end_date'] - harvest_time['start_date']
                    )
                    difference_times_list.append(difference_time.total_seconds())

                # Obtener el promedio de tiempos
                average_list_timers = (
                    sum(difference_times_list) / len(difference_times_list)
                )
                
                if current_difference_time < average_list_timers:
                    restant_time = average_list_timers - current_difference_time
                else:
                    restant_time = self.calculate_time_by_quantity(harvest, current_difference_time)
            else:
                restant_time = self.calculate_time_by_quantity(harvest, current_difference_time)

            if restant_time:
                days, remainder = divmod(restant_time, 86400)  # Dias
                hours, remainder = divmod(remainder, 3600)  # Horas
                minutes, seconds = divmod(remainder, 60)  # Minutos

                harvest.remaining_time = f"{int(days)} d, {int(hours)} h, {int(minutes)} m, {int(seconds)} s"

    def calculate_time_by_quantity(self, harvest, current_difference_time):
        if harvest.progress_count > 0:
            tiempo_restante = harvest.progress_count/current_difference_time
            unidades_restantes = harvest.counter_total_resources - harvest.progress_count
            end_oper = unidades_restantes / tiempo_restante
            return end_oper

    def count_total_resources(self, format_source, file=None):
        from harvester.functions.harvester import prepare_file

        harvest = Harvest.objects.get(group_id=self.group_id)
        record_count = 0
        record_count_temp = 0
        if not harvest.counter_total_resources:
            try:
                if 'http' in format_source:
                    sickle_instance = Sickle(
                        format_source,
                        iterator=OAIResponseIterator,
                        verify=False,
                        headers={"user-agent": "PostmanRuntime/7.25.0"},
                    )
                    try:
                        # Obtener respuestas de Sickle
                        sickle_responses = sickle_instance.ListRecords(
                            set=self.a_set[0], metadataPrefix="oai_dc", ignore_deleted=True
                        )

                        # Manejar la primera página
                        current_page = sickle_responses.next()
                        while True:
                            for element in current_page.xml.iter(tag="{*}record"):
                                record = Record(element, strip_ns=True)
                                if hasattr(record, "metadata"):
                                    record_count_temp += 1

                            # Intenta obtener la siguiente página
                            try:
                                current_page = sickle_responses.next()
                            except StopIteration:
                                break

                        record_count = record_count_temp


                    except NoRecordsMatch:
                        bbl_logger.error(_("Set vacío:"))
                else:
                    with prepare_file(file) as file_t:
                        if format_source == "marc_plain":
                            # Itera sobre cada registro
                            record_count = sum(1 for record in pymarc.MARCReader(file_t))
                        elif format_source == "marc_xml":
                            for i, elem in etree.iterparse(file_t, events=('end',)):
                                if elem.tag == '{http://www.loc.gov/MARC21/slim}record':
                                    record_count += 1
                        elif format_source == "csv":
                            reader = csv.DictReader(
                                io.TextIOWrapper(file_t, encoding="utf-8"),
                                delimiter=',',
                            )
                            # Itera sobre cada registro y omite las lineas vacias
                            record_count = sum(1 for row in reader if any(row.values()))

                harvest.counter_total_resources = record_count
                harvest.save()
                record_count = 0
                record_count_temp = 0

            except Exception as e:
                harvest.status = 2
                self.change_stage_by_step()
                bbl_logger.info(f'\033[1;33m Error en el conteo total de recursos: {e}')
                raise

    def set_calculate_progress(self, progress):
        self.progress = progress

    def get_calculate_progress(self, harvest):
        ''' Devuelve el total de recursos acumulado '''
        return harvest.progress_count + self.progress
