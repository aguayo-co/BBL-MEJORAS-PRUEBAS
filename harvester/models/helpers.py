"""Define helpers for models of the Harvester app."""

import hashlib
import logging
import re
import time
import urllib
from datetime import date
from urllib.parse import urlparse

import bleach
import roman_numerals
from constance import config
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Avg, Count, Prefetch, Subquery
from django.http import QueryDict
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format as date_format
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()  # pylint: disable=invalid-name

LONG_TEXT = 2000
SHORT_TEXT = 255
TINY_TEXT = 50

FIELDS_EQUIVALENCES_CHOICES = [
    ("type", _("tipo de contenido")),
    ("language", _("idioma")),
    ("rights", _("derechos")),
    ("subject", _("tema")),
    ("creator", _("autor")),
]
FIELDS_WITH_EQUIVALENCES = [field for field, name in FIELDS_EQUIVALENCES_CHOICES]
logger = logging.getLogger("")


class ContentResourceProcessor:
    """
    Accessor class to ContentResource data.

    It processes and outputs the data in a usable way.
    """

    DATE_PRECISSION = {
        "CENTURY": 0,
        "DECADE": 1,
        "CIRCA_YEAR": 2,
        "YEAR": 3,
        "MONTH": 4,
        "DAY": 5,
    }

    _author_regex = re.compile(
        r"""
        ^
        (?P<last_name>.+?)      # Capture anything before the first comma
        ,                       # First comma separates last name
        (?P<first_name>         # Create capture group for names
            (
                [^,]            # Capture anything that is not a comma,
                (?!\b[0-9]{4})  # if not followed by the beginning of a 4 numbered word
            )+                  # Capture at least once, and as many times as posible
        )
        """,
        re.VERBOSE,
    )

    _date_regex = re.compile(
        r"""
            (?<![0-9a-z])               # Must not be preceded by number or letter
            (?:
                (?P<dmy>[0-9]{1,2}/[0-9]{1,2}/[0-9]{4})         # dd/mm/yyyy date
                |                       # or
                (?P<iso>[0-9]{4}-[0-9]{1,2}-[0-9]{1,2})         # ISO date
                |                       # or
                (?P<slashes>[0-9]{4}/[0-9]{1,2}/[0-9]{1,2})     # Almost ISO
                |                       # or
                (?:
                    (?P<cy>c\.?)?       # is a Circa year.
                    (?P<y>[0-9]{4})     # 4 numbers
                )
                |                       # or
                (?P<d>[0-9]{3}[-?])     # 3 numbers, and 1 dash or question mark
                |                       # or
                (?P<c>[0-9]{2}-[-?])    # 2 numbers, 1 dash, and 1 dash or question mark
            )
            (?![0-9a-z])                # Must not be followed by a number or a letter
            """,
        re.X | re.I,
    )

    ezproxy_user = None

    def __init__(self, resource):
        """Store a reference to the resource."""
        self.resource = resource

        # Caches the queryset.
        self._mappings_querysets = {}

    def __dir__(self):
        """Include resource's attributes as available."""
        dir_data = super().__dir__()
        if self.resource:
            for field in self.resource._meta.get_fields():
                dir_data.append(field.name)

        return dir_data

    def __getattr__(self, name):
        """Get attribute from resource if one is not available locally."""
        suffix = "_processor"

        # Avoid recursion.
        # If asked for a `X_processor` attribute, then it does not exist.
        if name.endswith(suffix):
            self.attribute_error(name)

        # Find dedicated processors.
        method = f"{name}{suffix}"
        if hasattr(self, method):
            return getattr(self, method)()

        # If it is a mapped field, use mapping processor.
        if name in self.resource.FIELDS_WITH_EQUIVALENCES:
            return self.mapped_field_processor(name)

        # Run generic processor for any other property.
        try:
            value = getattr(self.resource, name)
        except AttributeError:
            self.attribute_error(name)

        return self._default_processor(value)

    @classmethod
    def attribute_error(cls, attr):
        """Raise an AttributeError exception."""
        msg = "'{0}' object has no attribute '{1}'"
        msg = msg.format(cls.__name__, attr)
        raise AttributeError(msg)

    def creator_processor(self):
        """
        Return URL to image for current resource type.

        Should try to return the creator as:
        <Names> <Last Name(s)>

        For instance:
        - López Perez, Mateo -> Mateo López Perez
        - López Perez, Mateo, 1985- -> Mateo López Perez
        - López Perez, Mateo, 1985-2018 -> Mateo López Perez
        - Mateo López Perez -> Mateo López Perez
        - López Perez Mateo -> López Perez Mateo
        """
        if self.resource.creator.exists():
            creator_value = self.resource.creator.first().original_value

            if self.resource.creator.first().equivalence is not None:
                creator_value = self.resource.creator.first().equivalence.name

            result = self._author_regex.match(creator_value)
            if result is not None:
                first_name = result.group("first_name").strip()
                last_name = result.group("last_name").strip()
                return f"{first_name} {last_name}".strip()
            return creator_value
        return ""

    def average_rating_processor(self):
        """Return the avarage rating for the resource."""
        return self.resource.review_set.aggregate(average_rating=Avg("rating"))[
            "average_rating"
        ]

    @staticmethod
    def resolve_dynamic_image(values, capture, replace_string):
        """Extract elements from a field to build a dynamic url."""
        pattern = re.compile(capture)
        for value in values:
            try:
                if pattern.search(value) is not None:
                    replaced_url = pattern.sub(
                        r"{}".format(replace_string.replace("$", "\\")),
                        value,
                        pattern.groups,
                    )
                    URLValidator()(replaced_url)
                    return value, replaced_url
            except (ValidationError, re.error):
                continue
        return None, None

    def image_processor(self):
        """
        Return URL to image for current resource type.

        If an image is present in the resource, return it. If not, use a
        default image based on the type of resource.
        """
        dynamic_image_config = self.resource.data_source.dynamic_image
        dynamic_image = None
        if dynamic_image_config:
            _matched_value, dynamic_image = self.resolve_dynamic_image(
                getattr(self.resource, dynamic_image_config["field"]),
                dynamic_image_config["capture_expression"],
                dynamic_image_config["replace_expression"],
            )
        if dynamic_image:
            return dynamic_image

        image = self._default_processor(self.resource.images)
        if image:
            return image

        type_value = self._mapped_field_processor("type")
        if (
            getattr(type_value, "equivalence", None)
            and type_value.equivalence.icon_class
        ):
            image_name = f"type-{slugify(type_value.equivalence.icon_class)}"
        else:
            image_name = "no-image"
        return static(f"biblored/img/resource/{image_name}.svg")

    @classmethod
    def _date_with_precission(cls, value):
        """Return the date and its precission."""
        matches = cls._date_regex.finditer(value)

        date_instance = None
        precission = None
        count = 0
        for match in matches:
            count += 1

            if precission is not None:
                # We only need the first matched year
                # But we need to now if more than one match was found.
                # If we got here, we already went through the first match
                # and we now know we have more than 1.
                # If so, select the lowest precission.
                precission = min(precission, cls.DATE_PRECISSION["CIRCA_YEAR"])
                break

            if match["iso"] or match["slashes"] or match["dmy"]:
                split_by = "-" if match["iso"] else "/"
                split_value = match["iso"] or match["slashes"] or match["dmy"]
                matches = split_value.split(split_by)
                if match["dmy"]:
                    day, month, year = matches
                else:
                    year, month, day = matches
                year = int(year)
                if year > 0:
                    try:
                        date_instance = date(year, int(month), int(day))
                    except ValueError:
                        date_instance = date(year, 1, 1)
                        precission = cls.DATE_PRECISSION["CIRCA_YEAR"]
                    else:
                        precission = cls.DATE_PRECISSION["DAY"]

                continue

            if match["y"]:
                year = int(match["y"])
                if year > 0:
                    date_instance = date(year, 1, 1)
                    precission = cls.DATE_PRECISSION["YEAR"]
                    if match["cy"]:
                        precission = cls.DATE_PRECISSION["CIRCA_YEAR"]
                continue

            if match["d"]:
                year = int(match["d"][:3]) * 10
                if year > 0:
                    date_instance = date(year, 1, 1)
                    precission = cls.DATE_PRECISSION["DECADE"]
                continue

            if match["c"]:
                year = int(match["c"][:2]) * 100
                if year > 0:
                    date_instance = date(year, 1, 1)
                    precission = cls.DATE_PRECISSION["CENTURY"]
        logger.info("[DATE] 1:instance %s, precission %s", date_instance, precission)

        return date_instance, precission

    def date_processor(self):
        """Return a date instance if one is available."""
        date_value = self._default_processor(self.resource.date)
        if not date_value or date_value is None:
            logger.info("[DATE] 1:No date value found for %s", self.resource.pk)
            return None

        date_instance, __ = self._date_with_precission(date_value)

        if not date_instance or date_instance is None:
            logger.info("[DATE] 2:No date value found for %s", self.resource.pk)
            return None

        logger.info(
            "[DATE] 3:Date value found for %s, %s", self.resource.pk, date_instance
        )
        return date_instance

    def formatted_date_processor(self):
        """
        Format the date as year or full date.

        Dates might not be specific enough, so the human readable
        format must denote that.

        Century precission is returned in roman numerals.
        Ranges are denoted with "Ca." (circa).
        Anything else just the year.
        """
        date_value = self._default_processor(self.resource.date)
        if not date_value:
            return None

        date_instance, precission = self._date_with_precission(date_value)

        if not date_instance:
            return None

        type_value = self._mapped_field_processor("type")
        if (
            precission >= self.DATE_PRECISSION["DAY"]
            and type_value
            and type_value.equivalence
            and type_value.equivalence.full_date
            or type_value.equivalence.full_date
        ):
            return date_format(date_instance, "d/m/Y")

        year = date_instance.year

        # https://www.joc.com/how-count-centuries_19970102.html
        # https://stackoverflow.com/a/46356843
        if precission == self.DATE_PRECISSION["CENTURY"]:
            century = roman_numerals.convert_to_numeral((year - 1) // 100 + 1)
            return _("Century %(century)s") % {"century": century}

        if precission <= self.DATE_PRECISSION["CIRCA_YEAR"]:
            return f"Ca. {year}"

        return str(year)

    def description_processor(self):
        """Clean description from undesired HTML."""
        if (
            not self.resource.description
            or self.resource.description is None
            or self.resource.description[0] is None
        ):
            return ""

        return mark_safe(bleach.clean(self.resource.description[0], strip=True))

    def subject_processor(self):
        """Return mapped value for subject with search urls."""
        # Caches the queryset.
        if "subject" not in self._mappings_querysets:
            self._mappings_querysets["subject"] = self.resource.subject.all()
        subjects = self._mappings_querysets["subject"]

        if not subjects:
            return None

        processed_subjects = {}

        for subject in subjects:
            if not subject.equivalence:
                processed_subjects[subject.DEFAULT_MAPPING] = None
                continue
            processed_subjects[subject.equivalence.name] = (
                subject.equivalence.search_url
            )

        return processed_subjects

    def _mapped_field_processor(self, field):
        """Return first equivalence of value for given field."""
        # Caches the queryset.
        if field not in self._mappings_querysets:
            self._mappings_querysets[field] = getattr(self.resource, field).all()[:1]
        values = self._mappings_querysets[field]

        if not values:
            return None

        return values[0]

    def mapped_field_processor(self, field):
        """Return mapped value for given field."""
        value = self._mapped_field_processor(field)

        if not value:
            return None

        return value.equivalence.name if value.equivalence else value.DEFAULT_MAPPING

    @staticmethod
    def _default_processor(value):
        """Return first element of list if posible, or original value."""
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None

        if isinstance(value, str):
            value = value.strip()

        return value

    @staticmethod
    def ezproxy_link(url, ezproxy_user):
        """Generate an EZProxy link for the given url and user_id."""
        packet = f"$u{int(time.time())}$e"
        md5_payload = hashlib.md5(
            f"{config.EZPROXY_SECRET}{ezproxy_user}{packet}".encode("utf-8")
        ).hexdigest()
        ticket = urllib.parse.quote(md5_payload + packet)
        query = f"user={ezproxy_user}&ticket={ticket}&url={url}"
        return f"{config.EZPROXY_SERVER_URL}/login?{query}"

    def url_processor(self, user=None):
        """
        Return a tuple with information to access the resource.

        The tuple includes a URL and a boolean indicating wether it is external or not.
        If the resource is accessed through EZProxy, the URL is for the EZProxy.

        A URL for the login page is return for resources that require a logged user.
        """
        url = self._default_processor(self.resource.urls)

        if not url or url is None:
            return None

        if not self.is_exclusive:
            return (url, True)

        from expositions.models import DomainsPassModel

        domains = []
        for domain in DomainsPassModel.objects.all():
            result_domain = urlparse(domain.domain)
            domains.append(result_domain.netloc)

        url_real = urlparse(url)

        if url_real.netloc in domains:
            return (url, True)

        # A User is available. Create link.
        if user.is_authenticated and user.is_megared:
            ezproxy_user = f"{user.country.dian_code}{user.document}"
            return (self.ezproxy_link(url, ezproxy_user), True)

        # No User is available. Link to Login.
        query = QueryDict(mutable=True)
        query[REDIRECT_FIELD_NAME] = f"{self.resource.get_absolute_url()}?external"
        query["exclusive"] = ""
        query_string = query.urlencode()
        login_url = reverse("login")
        return (f"{login_url}?{query_string}", False)

    def is_exclusive_processor(self):
        """Return if a resource belongs to a exclusive data source."""
        return self.resource.data_source.exclusive is True

    def citation_processor(self):
        """
        Return a tuple with with information to create the Bibliographic citation.

        The first value is the template for the citation, and the second value is
        relative url for the resource that is being cited.

        The cite can then be fully created by converting the relative url to absolute
        url like this:

        `
        citation, url = processed_data.citation
        return citation % request.build_absolute_uri(url)
        `
        """
        cite = ""

        url = reverse("content_resource", args=[self.resource.pk])
        today = timezone.now().date()

        # Creator
        if self.creator:
            cite += f"{self.creator}, "

        # Title
        cite += f'"{self.title}", '

        type_value = self._mapped_field_processor("type")
        if type_value.equivalence and type_value.equivalence.cite_type == "periodical":
            # TODO de donde se toma este nombre de publicación? es diferente al título?
            cite += f"{self.title}, "

        # City
        if self.coverage:
            cite += f"{self.coverage}:"
        else:
            cite += "-:"

        # Publisher
        if self.publisher:
            cite += f"{self.publisher}, "
        else:
            cite += "-, "

        # Date
        if self.date:
            cite += f"{self.date.year}. "
        else:
            cite += "-. "

        cite += (
            "Consultado en línea en la Biblioteca Digital de Bogotá (%s), "
            f"el día {today}. "
        )
        return cite, url

    def group_hash_processor(self):
        """Calculate hash of the group hash."""
        fields = ResourceGroup.grouping_fields + ResourceGroup.mapping_grouping_fields
        default_hash = f"pk-{self.pk}"
        for field in ResourceGroup.grouping_fields:
            # If no value for some field, use no_hash.
            try:
                getattr(self.resource, field)[0]
            except IndexError:
                return default_hash
            except TypeError:
                return default_hash

        # Filter by mapping fields.
        for field in ResourceGroup.mapping_grouping_fields:
            # If no value for some field, use no_hash.
            try:
                # Fields should have been prefetched.
                # Use list to avoid an additional query.
                list(getattr(self.resource, field).all())[0].equivalence
            except IndexError:
                return default_hash
            except AttributeError:
                return default_hash

        if self.resource.data_source.online_resources:
            return hash(tuple(getattr(self, field) for field in fields) + ("NO",))
        return hash(tuple(getattr(self, field) for field in fields))


class ResourceGroup:
    """Accessor to grouped resources."""

    grouping_fields = ["creator", "title"]
    mapping_grouping_fields = ["language", "type"]

    # Use for caching querysets.
    _resources_queryset = None
    _sources_queryset = None

    def __init__(self, resource):
        """Set parent resource and grouping queryset."""
        self.resource = resource

    def get_resource_filters(self):
        """Return filters to find grouped ContentResources."""
        if not self.resource.calculated_group_hash:
            return {"pk": self.resource.pk}

        # Filter by hash.
        return {"calculated_group_hash": self.resource.calculated_group_hash}

    def get_resources_queryset(self):
        """Return a queryset to get grouped resources."""
        if self._resources_queryset is None:
            # Save the queryset to use cached queries.
            resource_filters = self.get_resource_filters()
            self._resources_queryset = self.resource.__class__.objects.visible().filter(
                **resource_filters
            )

        return self._resources_queryset

    def get_sources_queryset(self):
        """Return a queryset to get sources for grouped resources."""
        if self._sources_queryset is None:
            DataSource = self.resource._meta.get_field(  # pylint: disable=invalid-name
                "data_source"
            ).related_model

            # Save the queryset to use cached queries.
            self._sources_queryset = DataSource.objects.filter(
                id__in=self.get_resources_queryset().values("data_source")
            ).prefetch_related(
                "schedule_set",
                Prefetch(
                    "contentresource_set",
                    queryset=self.get_resources_queryset(),
                    to_attr="resources",
                ),
            )
        return self._sources_queryset

    @property
    def sources(self):
        """
        Return a list of the queryset result.

        Evaluating the queryset ensures results are cached. Multiple access to
        this property won't reevaluate the query.
        """
        return list(self.get_sources_queryset())

    @property
    def is_grouped(self):
        """Return True if there are 2 or more resources for this group."""
        return (
            self.resource.data_source.online_resources is False
            and self.get_resources_queryset().count() > 1
        )

    @property
    def online_sources(self):
        """Return a list of DataSources which have online Resources."""
        return [source for source in self.sources if source.online_resources]

    @property
    def offline_sources(self):
        """Return a list of DataSources which do not have online Resources."""
        return [source for source in self.sources if not source.online_resources]

    @property
    def resources(self):
        """Return a list of all the resources for the group."""
        resources = []
        for source in self.sources:
            for resource in source.resources:
                resources.append(resource)
        return resources

    @property
    def online_resources(self):
        """Return a list of all the online resources for the group."""
        resources = []
        for source in self.online_sources:
            for resource in source.resources:
                resources.append(resource)
        return resources

    @property
    def offline_resources(self):
        """Return a list of all the offline resources for the group."""
        resources = []
        for source in self.offline_sources:
            for resource in source.resources:
                resources.append(resource)
        return resources


class RelatedResource:
    """Accessor to related resources (similar resources that matches its subjects)."""

    # User for which related queries should be limited to.
    related_for_user = None
    # Cached queryset for by_reads.
    _by_reads = None
    # Cached queryset for resources.
    _resources = None

    def __init__(self, resource):
        """Set parent resource and related queryset."""
        self.resource = resource

    def related_by_subjet_queryset(self):
        """Return a queryset for related resources by subject."""
        equivalence_list = self.resource.subject.exclude(
            equivalence__isnull=True
        ).values_list("equivalence", flat=True)
        equivalence_list = [equivalence for equivalence in equivalence_list]
        related_query = (
            self.resource.__class__.objects.visible()
            .exclude(pk=self.resource.pk)
            .filter(
                subject__equivalence__in=equivalence_list,
                data_source__online_resources=True,
            )
        )
        return related_query

    def get_related_queryset(self):
        """
        Return a queryset to get related resources based on current resource.

        Rules:
        - Online Resources
        - Same Subject(s)
        - Not same Title
        - Order by Data Source Relevance and Collections
        """
        return (
            self.related_by_subjet_queryset()
            .filter(collectionandresource__isnull=False)
            .annotate(collection__count=Count("collection"))
            .order_by("data_source__relevance", "-collection__count")[:2]
        )

    def get_by_reads_queryset(self):
        """Return a user's most visited resources related to current resource."""
        if not self.related_for_user:
            self.resource.__class__.objects.none()

        return (
            self.related_by_subjet_queryset()
            .filter(hitcount__hit__user=self.related_for_user)
            .annotate(user_hits=Count("hitcount__hit"))
            .order_by("data_source__relevance", "-user_hits")[:4]
        )

    @property
    def resources(self):
        """Return a list of related resources."""
        if self._resources is None:
            self._resources = self.get_related_queryset()

        return list(self.get_related_queryset())

    @property
    def by_reads(self):
        """Return a list of related resources."""
        if not self.related_for_user:
            return []

        if getattr(self._by_reads, "user", None) is not self.related_for_user:
            self._by_reads = {
                "user": self.related_for_user,
                "queryset": self.get_by_reads_queryset()[:4],
            }

        return list(self._by_reads["queryset"])
