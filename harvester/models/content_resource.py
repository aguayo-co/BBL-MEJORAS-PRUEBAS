"""Models definitions for Content Resource."""

import datetime
import hashlib
import inspect
import logging
import re
from collections import namedtuple
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import BooleanField, DateField, DateTimeField
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.models import Schedule
from wagtail.search import index

from wagtailmodelchooser import register_model_chooser
from wagtail.search.backends import get_search_backend

from harvester.exceptions import InvalidModelInstance
from hitcount.models import HitCount, HitCountMixin
from resources.fields import IntegerCachedField, TextCachedField
from resources.helpers import unparallel
from resources.models import TimestampModel

from ..managers import ContentResourceManager, OutdatedContentResourceManager
from .helpers import (
    FIELDS_EQUIVALENCES_CHOICES,
    FIELDS_WITH_EQUIVALENCES,
    RelatedResource,
    ResourceGroup,
)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

processed_data_fields = {"date": None, "group_hash": None}
ProcessedData = namedtuple(
    "ProcessedData",
    processed_data_fields.keys(),
    defaults=(None,) * len(processed_data_fields.keys()),
)


class ContentResourceCalculatedFieldsMixin(models.Model):
    """Model for calculated fields, acts as a drop-in replacement for processed_data."""

    PREFIX = "calculated_"
    # Calculated Fields
    calculated_date = DateField(null=True, editable=False)
    calculated_group_hash = models.TextField(
        verbose_name=_("Hash de Agrupamiento"), null=True, editable=False
    )

    # Required Fields
    _resource_processor = None
    # No se nombra como 'calculated_at' para que no se confunda con un campo calculado
    calculation_at = DateTimeField(null=True, editable=False)
    force_calculation = BooleanField(default=False, editable=False)

    outdated_objects = OutdatedContentResourceManager()

    @property
    def resource_processor(self):
        """Return a Resource Processor for current Resource."""
        from harvester.models.helpers import ContentResourceProcessor

        return ContentResourceProcessor(self)

    @property
    def needs_recalculation(self):
        """Check if the calculated fields need to be recalculated."""
        if (
            not self.calculation_at
            or self.force_calculation
            or self.calculation_at < getattr(self, "updated_at", timezone.now())
        ):
            return True
        return False

    def calculate_fields(self):
        """Get the processed field and store in the calculated field."""
        if self.needs_recalculation:
            for field_name in self.get_calculated_fields():
                setattr(
                    self,
                    field_name,
                    getattr(
                        self.resource_processor, field_name.replace(self.PREFIX, "")
                    ),
                )
            self.calculation_at = timezone.now()
            self.force_calculation = False
        return self.get_calculated_fields() + ["calculation_at", "force_calculation"]

    @classmethod
    def get_calculated_fields(cls):
        """Return the list of fields to recalculate."""
        return [
            field.name
            for field in cls._meta.get_fields(include_parents=False)
            if field.name.startswith(cls.PREFIX)
        ]

    @property
    def processed_data(self):
        """Return an accessor to processed data and resource processor properties."""
        processed_data_fields.update(
            {
                field.name.replace(self.PREFIX, ""): getattr(self, field.name)
                for field in self._meta.get_fields(include_parents=False)
                if field.name.startswith(self.PREFIX)
                and getattr(self, field.name, None) is not None
            }
        )
        ProcessedData.__getattr__ = self.resource_processor.__getattr__
        # Pass Methods
        for method_name, method in inspect.getmembers(
            self.resource_processor, predicate=inspect.ismethod
        ):
            if not method_name.startswith("__"):
                setattr(ProcessedData, method_name, method)
        return ProcessedData(**processed_data_fields)

    class Meta:
        """Options for the ContentResourceCalculatedFieldsMixin class."""

        abstract = True


@register_model_chooser
class ContentResource(
    index.Indexed,
    TimestampModel,
    HitCountMixin,
    ContentResourceCalculatedFieldsMixin,
):
    """
    A Content Resource is a single element such a book, an image, a movie, a film.

    Most fields are based on DublinCore, but it does not follow the standard exactly.
    """

    FIELDS_EQUIVALENCES_CHOICES = FIELDS_EQUIVALENCES_CHOICES
    FIELDS_WITH_EQUIVALENCES = FIELDS_WITH_EQUIVALENCES

    sets = models.ManyToManyField(
        "harvester.Set",
        through="SetAndResource",
        through_fields=("resource", "set"),
    )

    abstract = ArrayField(models.TextField(), null=True, verbose_name=_("resumen"))
    accessRights = ArrayField(
        models.TextField(), null=True, verbose_name=_("acceso correcto")
    )
    accrualMethod = ArrayField(
        models.TextField(), null=True, verbose_name=_("método acumulación")
    )
    accrualPeriodicity = ArrayField(
        models.TextField(), null=True, verbose_name=_("periodicidad de acumulación")
    )
    accrualPolicy = ArrayField(
        models.TextField(), null=True, verbose_name="política de acumulación"
    )
    alternative = ArrayField(
        models.TextField(), null=True, verbose_name=_("alternativa")
    )
    audience = ArrayField(models.TextField(), null=True, verbose_name=_("audiencia"))
    available = ArrayField(models.TextField(), null=True, verbose_name=_("disponible"))
    bibliographicCitation = ArrayField(
        models.TextField(), null=True, verbose_name=_("cita bibliográfica")
    )
    conformsTo = ArrayField(
        models.TextField(), null=True, verbose_name=_("de acuerdo a")
    )
    contributor = ArrayField(
        models.TextField(), null=True, verbose_name=_("colaborador")
    )
    coverage = ArrayField(models.TextField(), null=True, verbose_name=_("cobertura"))
    created = ArrayField(models.TextField(), null=True, verbose_name=_("creado"))
    date = ArrayField(models.TextField(), null=True, verbose_name=_("fecha"))
    dateAccepted = ArrayField(
        models.TextField(), null=True, verbose_name=_("fecha aceptación")
    )
    dateCopyrighted = ArrayField(
        models.TextField(), null=True, verbose_name=_("fecha derechos de autor")
    )
    dateSubmitted = ArrayField(
        models.TextField(), null=True, verbose_name=_("fecha enviado")
    )
    description = ArrayField(
        models.TextField(), null=True, verbose_name=_("descripción")
    )
    digitalFormat = ArrayField(
        models.TextField(), null=True, verbose_name=_("formato digital")
    )
    educationLevel = ArrayField(
        models.TextField(), null=True, verbose_name=_("nivel educativo")
    )
    extent = ArrayField(models.TextField(), null=True, verbose_name=_("grado"))
    format = ArrayField(models.TextField(), null=True, verbose_name=_("formato"))
    hasFormat = ArrayField(
        models.TextField(), null=True, verbose_name=_("tiene formato")
    )
    hasPart = ArrayField(models.TextField(), null=True, verbose_name=_("tiene parte"))
    hasVersion = ArrayField(
        models.TextField(), null=True, verbose_name=_("tiene versión")
    )
    dynamic_identifier = TextCachedField(
        null=True, verbose_name=_("identificador dinámico")
    )
    identifier = ArrayField(models.TextField(), verbose_name=_("identificador"))
    instructionalMethod = ArrayField(
        models.TextField(), null=True, verbose_name=_("método de instrucción")
    )
    isFormatOf = ArrayField(
        models.TextField(), null=True, verbose_name=_("es formato de")
    )
    isPartOf = ArrayField(models.TextField(), null=True, verbose_name=_("es parte de"))
    isReferencedBy = ArrayField(
        models.TextField(), null=True, verbose_name=_("es referenciado por")
    )
    isReplacedBy = ArrayField(
        models.TextField(), null=True, verbose_name=_("es reemplazado por")
    )
    isRequiredBy = ArrayField(
        models.TextField(), null=True, verbose_name=_("es requerido por")
    )
    issued = ArrayField(models.TextField(), null=True, verbose_name=_("emitido"))
    isVersionOf = ArrayField(
        models.TextField(), null=True, verbose_name=_("es versión de")
    )
    license = ArrayField(models.TextField(), null=True, verbose_name=_("licencia"))
    mediator = ArrayField(models.TextField(), null=True, verbose_name=_("mediador"))
    medium = ArrayField(models.TextField(), null=True, verbose_name=_("medio"))
    modified = ArrayField(models.TextField(), null=True, verbose_name=_("modificado"))
    provenance = ArrayField(
        models.TextField(), null=True, verbose_name=_("procedencia")
    )
    publisher = ArrayField(models.TextField(), null=True, verbose_name=_("editor"))
    references = ArrayField(
        models.TextField(), null=True, verbose_name=_("referencias")
    )
    relation = ArrayField(models.TextField(), null=True, verbose_name=_("relación"))
    replaces = ArrayField(models.TextField(), null=True, verbose_name=_("reemplaza"))
    requires = ArrayField(models.TextField(), null=True, verbose_name=_("requiere"))
    rightsHolder = ArrayField(
        models.TextField(), null=True, verbose_name=_("titular de los derechos")
    )
    source = ArrayField(models.TextField(), null=True, verbose_name=_("fuente"))
    spatial = ArrayField(models.TextField(), null=True, verbose_name=_("espacial"))
    tableOfContents = ArrayField(
        models.TextField(), null=True, verbose_name=_("tabla de contenidos")
    )
    temporal = ArrayField(models.TextField(), null=True, verbose_name=_("temporal"))
    title = ArrayField(models.TextField(), null=True, verbose_name=_("título"))
    topographicNumber = ArrayField(
        models.TextField(), null=True, verbose_name=_("número topográfico")
    )
    valid = ArrayField(models.TextField(), null=True, verbose_name=_("válido"))

    creator = models.ManyToManyField(
        "ContentResourceEquivalence",
        through="CreatorEquivalenceRelation",
        blank=True,
        related_name="creator_resources",
        verbose_name=_("autor"),
    )
    type = models.ManyToManyField(
        "ContentResourceEquivalence",
        through="TypeEquivalenceRelation",
        blank=True,
        related_name="type_resources",
        verbose_name=_("tipo"),
    )
    subject = models.ManyToManyField(
        "ContentResourceEquivalence",
        through="SubjectEquivalenceRelation",
        blank=True,
        related_name="subject_resources",
        verbose_name=_("tema"),
    )
    rights = models.ManyToManyField(
        "ContentResourceEquivalence",
        through="RightsEquivalenceRelation",
        blank=True,
        related_name="rights_resources",
        verbose_name=_("derechos"),
    )
    language = models.ManyToManyField(
        "ContentResourceEquivalence",
        through="LanguageEquivalenceRelation",
        blank=True,
        related_name="language_resources",
        verbose_name=_("idioma"),
    )

    data_source = models.ForeignKey(
        "harvester.DataSource",
        on_delete=models.CASCADE,
        null=False,
        editable=False,
        verbose_name=_("fuente de datos"),
    )
    visible = models.BooleanField(
        default=True,
        verbose_name=_("visibilidad"),
        help_text=_("Permite mostrar u ocultar un el recurso en el sitio."),
    )
    collection_count = IntegerCachedField(
        null=True, verbose_name=_("Número de colecciones")
    )

    objects = ContentResourceManager()

    # WagTail search fields.
    search_fields = [
        index.FilterField("id"),
        index.SearchField(
            "title",
            boost=4,
            es_extra={
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "suggestions": {
                        "type": "text",
                        "analyzer": "suggestions",
                        "search_analyzer": "standard",
                    },
                },
                "analyzer": "lowercase-asciifolding",
                "copy_to": ["didyoumean"],
            },
        ),
        index.AutocompleteField(
            "title",
            es_extra={
                "analyzer": "lowercase-asciifolding",
                "copy_to": ["didyoumean"],
            },
        ),
        index.SearchField(
            "truncated_description",
            boost=2,
            es_extra={
                "type": "text",
                "analyzer": "lowercase-asciifolding",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": ["didyoumean", "description"],
            },
        ),
        index.FilterField("date_field"),
        index.RelatedFields("sets", [index.SearchField("name")]),
        index.AutocompleteField("created_at"),
        index.SearchField(
            "creator_field",
            boost=4,
            es_extra={
                "type": "text",
                "analyzer": "lowercase-asciifolding",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": ["didyoumean"],
            },
        ),
        index.RelatedFields(
            "data_source",
            [
                index.FilterField("id"),
                index.FilterField("name"),
                index.FilterField("relevance"),
                index.FilterField("online_resources"),
            ],
        ),
        index.SearchField(
            "calculated_group_hash",
            es_extra={
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
        ),
        index.FilterField("has_visible_set"),
        index.SearchField(
            "didyoumean",
        ),
        index.AutocompleteField("didyoumean"),
        index.FilterField("language_field"),
        index.SearchField(
            "publisher",
            es_extra={
                "type": "text",
                "analyzer": "lowercase-asciifolding",
                "fields": {"keyword": {"type": "keyword"}},
            },
        ),
        index.FilterField("rights_field"),
        index.SearchField(
            "subject_field",
            es_extra={
                "type": "text",
                "analyzer": "lowercase-asciifolding",
                "fields": {"keyword": {"type": "keyword"}},
                "copy_to": ["didyoumean"],
            },
        ),
        index.FilterField("type_field"),
        index.SearchField("updated_at"),
        index.FilterField("visible"),
        index.FilterField("data_source_relevance"),
        index.FilterField("data_source_id"),
    ]

    _processed_data = None
    _resource_group = None
    _related = None

    hitcount = GenericRelation(
        HitCount, object_id_field="object_pk", related_query_name="+"
    )

    class Meta(TimestampModel.Meta):
        """Define properties for ContentResource."""

        verbose_name = _("recurso de contenido")
        verbose_name_plural = _("recursos de contenido")
        permissions = (("delete_in_background", _("Borrado en segundo plano")),)
        indexes = TimestampModel.Meta.indexes + [
            models.Index(fields=["title"]),
            models.Index(fields=["dynamic_identifier_cached", "data_source"]),
            models.Index(fields=["dynamic_identifier_expired"]),
            models.Index(fields=["dynamic_identifier_expiration"]),
            models.Index(
                fields=[
                    "dynamic_identifier_expired",
                    "dynamic_identifier_expiration",
                    "data_source",
                ]
            ),
            models.Index(
                fields=["dynamic_identifier_expired", "dynamic_identifier_expiration"]
            ),
            models.Index(fields=["visible"]),
            models.Index(fields=["calculated_group_hash"]),
        ]

    @property
    def type_field(self):
        return list(self.type.all().values_list("original_value", flat=True))

    @property
    def date_field(self):
        return self.processed_data.date

    @property
    def subject_field(self):
        subjects_list = list(
            self.subject.all().values_list("original_value", flat=True)
        )
        subjects_from_processed_data = list(self.processed_data.subject.keys())
        subjects_from_processed_data = [
            str(key) for key in subjects_from_processed_data
        ]

        subjects = subjects_list + subjects_from_processed_data
        return subjects

    @property
    def rights_field(self):
        return list(self.rights.all().values_list("original_value", flat=True))

    @property
    def language_field(self):
        return list(self.language.all().values_list("original_value", flat=True))

    @property
    def creator_field(self):
        return self.processed_data.creator

    @property
    def data_source_id(self):
        return int(self.data_source.pk)

    @property
    def has_visible_set(self):
        existing_sets = self.sets.filter(data_source=self.data_source_id)
        has_visible = False
        for current_set in existing_sets:
            if current_set.visible:
                has_visible = True
        # For the first time indexing
        if len(existing_sets) == 0:
            has_visible = True
        return has_visible

    @property
    def data_source_relevance(self):
        return int(self.data_source.relevance)

    @property
    def didyoumean(self):
        return ""

    @property
    def resource_group(self):
        """Return an instance of ResourceGroup for the current resource."""
        if not self._resource_group:
            self._resource_group = ResourceGroup(self)
        return self._resource_group

    @property
    def related(self):
        """Return an instance of RelatedResource for the current resource."""
        if not self._related:
            self._related = RelatedResource(self)
        return self._related

    @property
    def truncated_description(self):
        if self.processed_data.description not in [None, ""]:
            if len(self.processed_data.description) > 1000:
                return f"{self.processed_data.description[:1000]}..."
            return self.processed_data.description
        return self.processed_data.description

    def get_absolute_url(self):
        """Return url for current instance."""
        return reverse("content_resource", args=[self.pk])

    @property
    def urls(self):
        """Return all urls found in identifier."""
        # Simulate behavior of other Array fields.
        if not self.identifier:
            return self.identifier

        urls = []
        for identifier in self.identifier:
            try:
                URLValidator()(str(identifier))
            except ValidationError:
                pass
            else:
                urls.append(str(identifier))

        return urls

    @property
    def images(self):
        """Return all urls to images found in identifier."""
        # Leverage urls property which filters valid URLs already.
        if not self.urls:
            return self.urls

        images = []
        allowed_extensions = ["jpg", "jpeg", "png", "gif"]
        for url in self.urls:
            # Check if the full URL, including query string, ends in one of the
            # accepted extensions.
            # Some images come in a format like:
            # http://domain.com/path?query=image.jpg
            try:
                extension = url[url.rindex(".") + 1 :]
            except ValueError:
                pass
            else:
                if extension in allowed_extensions:
                    images.append(url)
                    continue

            # Now check just the path.
            extension = Path(urlparse(url).path).suffix[1:].lower()
            if extension in allowed_extensions:
                images.append(url)

        return images

    @staticmethod
    def calculate_hashed_identifier(identifiers):
        """Return the value for hashed_identifier based on identifiers."""
        identifiers = [
            str(x).strip() for x in identifiers if (x is not None and str(x).strip())
        ]
        if not identifiers:
            raise InvalidModelInstance
        return hashlib.sha1(repr(identifiers).encode("utf-8")).hexdigest()

    @staticmethod
    def calculate_dynamic_identifier(configs=None, resource_data=None):
        """
        Calculate the dynamic identifier for a resource using dynamic configs.

        Each captured group will be concatenated to generate a unique ID.
        If a regex or group fails, an `InvalidModelInstance` is raised.

        For each field, the first value of the field that matches the regex is used.
        """
        dynamic_identifier = []
        for config in configs:
            pattern = re.compile(config.capture_expression)
            if isinstance(resource_data, dict):
                values = resource_data.get(config.field, [])
            else:
                values = getattr(resource_data, config.field, [])

            # Ensure there is a value
            values = [] if values is None else values
            # Ensure values is a list or tuple
            values = values if isinstance(values, (list, tuple)) else [values]
            matches = None
            for value in values:
                matches = pattern.search(value)
                if matches:
                    dynamic_identifier.extend(matches.groups())
                    break
        dynamic_identifier = [
            identifier for identifier in dynamic_identifier if identifier is not None
        ]
        if not dynamic_identifier:
            raise InvalidModelInstance
        return "|".join(dynamic_identifier)

    @classmethod
    def calculate_identifier(cls, resource_data, configs):
        """Return the calculated identifier."""
        if not configs:
            try:
                identifiers = resource_data.identifier
            except AttributeError:
                identifiers = resource_data["identifier"]
            return cls.calculate_hashed_identifier(identifiers)
        return cls.calculate_dynamic_identifier(
            resource_data=resource_data, configs=configs
        )

    def update_cached_dynamic_identifier(self):
        """Update the Cached Hashed Identifier Field and set an expiration."""
        self.dynamic_identifier_cached = self.calculate_identifier(
            self, self.data_source.dynamicidentifierconfig_set.all()
        )
        self.dynamic_identifier_expiration = timezone.now() + datetime.timedelta(
            days=90
        )
        self.dynamic_identifier_expired = False

    def update_cached_collection_count(self):
        """Update the Cached Collection Count Field and set an expiration."""
        self.collection_count = self.collection_set.count()
        self.collection_count_expiration = timezone.now() + datetime.timedelta(days=15)
        self.collection_count_expired = False

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """Force refresh of dynamic identifier before saving."""
        if (
            update_fields is None
            or isinstance(update_fields, list)
            and "identifier" in update_fields
        ):
            self.update_cached_dynamic_identifier()
            if isinstance(update_fields, list):
                update_fields.extend(
                    [
                        "dynamic_identifier_cached",
                        "dynamic_identifier_expiration",
                        "dynamic_identifier_expired",
                    ]
                )
        super().save(force_insert, force_update, using, update_fields)

    @property
    def set_id(self):
        return self.sets.first().id

    def __str__(self):
        """Return a string representation of a Content Resource."""
        title = self.title[0] if self.title else ""
        return f"{title} - [{self.data_source}]"


@unparallel
def calculate_resource_fields_task(limit):
    """Execute the field's calculation task and schedule the next one."""
    return calculate_resource_fields(limit)


def schedule_resource_fields_calculation_task(limit=5000, minutes=5):
    """Schedule the next field's calculation task."""
    func = "harvester.models.content_resource.calculate_resource_fields_task"
    Schedule.objects.update_or_create(
        name=func,
        next_run=(timezone.now() + datetime.timedelta(minutes=minutes)),
        defaults={
            "name": _("Actualización de Campos Calculados"),
            "kwargs": {"limit": limit},
            "func": func,
            "minutes": minutes,
            "schedule_type": "I",
        },
    )


def calculate_resource_fields(limit):
    """Update all the calculated fields of outdated resources."""
    resources = ContentResource.outdated_objects.all()[:limit]
    updated_resources = []
    updated_fields = []
    batch_size = settings.TASK_PAGE_LENGTH

    # For Indexing
    backend = get_search_backend("default")
    search_index = backend.get_index_for_model(ContentResource)

    for resource in resources.iterator():
        resource.updated_at = timezone.now()
        updated_fields = resource.calculate_fields()
        updated_resources.append(resource)

        if len(updated_resources) >= batch_size:
            ContentResource.objects.bulk_update(updated_resources, updated_fields)
            search_index.add_items(ContentResource, updated_resources)
            updated_resources.clear()

    if updated_resources:
        ContentResource.objects.bulk_update(updated_resources, updated_fields)
        search_index.add_items(ContentResource, updated_resources)

    logger.info("Actualizados Campos Calculados de %s recursos", resources.count())
    return f"Actualizados Campos Calculados de {resources.count()} recursos"
