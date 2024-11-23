"""Define Model Managers for Harvester app."""
from collections import defaultdict

from caching.base import CachingQuerySet
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import Count, F, OneToOneRel, Prefetch, Q
from wagtail.search.queryset import SearchableQuerySetMixin


class VisibleQueryset(models.QuerySet):
    """Queryset that filters by visible elements by default."""

    def visible(self):
        """Limit queryset to visible elements."""
        return self.filter(visible=True)


class AnnotatedGroupsQueryset(VisibleQueryset):
    """Extend the Visible queryset."""

    # TODO esto es innecesario
    def annotate_groups(self):
        """Annotate concatenated collections groups id."""
        return self.annotate(
            groups_list=ArrayAgg("collections_groups__collections_group")
        )


class CollectionQueryset(AnnotatedGroupsQueryset):
    """Extend the Collection queryset."""

    def get_subclasses_excludes(self):
        """Return a set of OR conditions to exclude subclasses."""
        excludes = Q()
        for field in self.model._meta.get_fields(include_hidden=True):
            if isinstance(field, OneToOneRel):
                excludes |= Q(**{f"{field.name}__isnull": False})
        return excludes

    def exclude_subclasses(self):
        """
        Apply subclasses excludes to queryset.

        Any Collection that is also a SubClass will be excluded.
        """
        return self.exclude(self.get_subclasses_excludes())


class SetQueryset(AnnotatedGroupsQueryset):
    """Extend the Set queryset."""


class CollaborativeCollectionQueryset(AnnotatedGroupsQueryset):
    """Extend the Collection queryset."""

    def prefetch_active_collaborators(self):
        """Prefetch collaborators with status equal to 1."""
        from django.contrib.auth import get_user_model

        from .models import Collaborator

        User = get_user_model()  # pylint: disable=invalid-name

        return self.prefetch_related(
            Prefetch(
                "collaborators",
                queryset=User.objects.filter(
                    id__in=Collaborator.objects.filter(status=1).values("user")
                ),
                to_attr="collaborators_users",
            )
        )

    def annotate_active_collaborators_id(self):
        """Annotate collaborators id with status equal to 1."""
        return self.annotate(
            active_collaborators_id=ArrayAgg(
                "collaborator__user", filter=Q(collaborator__status=1)
            )
        )

    def annotate_requested_collaborators_id(self):
        """Annotate collaborators id with status equal to -2."""
        return self.annotate(
            requested_collaborators_id=ArrayAgg(
                "collaborator__user", filter=Q(collaborator__status=-2)
            )
        )

    def annotate_invited_collaborators_id(self):
        """Annotate collaborators id with status equal to -1."""
        return self.annotate(
            invited_collaborators_id=ArrayAgg(
                "collaborator__user", filter=Q(collaborator__status=-1)
            )
        )


class CollaborativeCollectionManager(
    models.Manager.from_queryset(CollaborativeCollectionQueryset)
):
    """Manager for CollaborativeCollection Model that uses (select|prefetch)_related."""

    def get_queryset(self):
        """Extend Queryset with (select|prefetch)_related."""
        queryset = super().get_queryset()
        queryset = (
            queryset.select_related("owner__profile")
            .annotate_active_collaborators_id()
            .annotate_requested_collaborators_id()
            .annotate_invited_collaborators_id()
            .prefetch_active_collaborators()
        )
        return queryset


class ContentResourceQueryset(SearchableQuerySetMixin, VisibleQueryset):
    """Extend ContentResources queryset."""

    @staticmethod
    def get_prefetch_equivalences():
        """Return Prefetches compatible with prefetch_related for Equivalences."""
        from .models import ContentResourceEquivalence

        return [
            Prefetch(
                "subject",
                queryset=ContentResourceEquivalence.objects.order_by(
                    "subjectequivalencerelation__position"
                ),
            ),
            Prefetch(
                "language",
                queryset=ContentResourceEquivalence.objects.order_by(
                    "languageequivalencerelation__position"
                ),
            ),
            Prefetch(
                "rights",
                queryset=ContentResourceEquivalence.objects.order_by(
                    "rightsequivalencerelation__position"
                ),
            ),
            Prefetch(
                "type",
                queryset=ContentResourceEquivalence.objects.order_by(
                    "typeequivalencerelation__position"
                ),
            ),
        ]

    def prefetch_equivalences(self):
        """Prefetch Equivalences."""
        return self.prefetch_related(*self.get_prefetch_equivalences())

    def visible(self):
        """Limit queryset to resources of visible sets."""
        from .models import Set

        return (
            super()
            .visible()
            .filter(id__in=Set.objects.visible().values("setandresource__resource_id"))
        )

    def by_type__count(self):
        """
        Count ContentResources by type.

        The first value of type is used to get the mapped type,
        and the final count is returned according to mapped types.
        """
        from .models import ContentResourceEquivalence

        queryset = (
            self.filter(
                Q(typeequivalencerelation__position=0)
                | Q(typeequivalencerelation__isnull=True)
            )
            .values("type__equivalence__name")
            .annotate(Count("pk"))
            .order_by("-pk__count")
        )
        types_count = defaultdict(int)
        for type_result in queryset:
            mapped_type = (
                type_result["type__equivalence__name"]
                or ContentResourceEquivalence.DEFAULT_MAPPING
            )
            types_count[mapped_type] += type_result["pk__count"]

        return dict(types_count)


class PromotedContentResourceQueryset(models.QuerySet):
    """Extend PromotedContentResource queryset."""

    def visible(self):
        """Make visible if ContentResources is visible."""
        return self.filter(resource__visible=True)


class ContentResourceManager(models.Manager.from_queryset(ContentResourceQueryset)):
    """Manager for ContentResource Model that uses (select|prefetch)_related."""

    def get_queryset(self):
        """Extend Queryset with (select|prefetch)_related."""
        queryset = (
            super()
            .get_queryset()
            .prefetch_related("data_source")
            .prefetch_equivalences()
        )

        return queryset


class OutdatedContentResourceManager(ContentResourceManager):
    """Manager for ContentResource Model that get outdated resources."""

    def get_queryset(self):
        """Extend Queryset to get resources with outdated data."""
        filters = Q()
        from .models import ResourceGroup

        for field in ResourceGroup.mapping_grouping_fields:
            position_filter = f"{field}equivalencerelation__position"
            equivalence_filter = (
                f"{field}equivalencerelation"
                "__contentresourceequivalence__equivalence__updated_at__gt"
            )
            mapping_filter = f"{field}equivalencerelation__contentresourceequivalence__updated_at__gt"  # noqa: E501
            filters |= Q(**{position_filter: 0}) & (
                Q(**{equivalence_filter: F("calculation_at")})
                | Q(**{mapping_filter: F("calculation_at")})
            )

        queryset = (
            super()
            .get_queryset()
            .filter(
                filters
                | Q(calculation_at__isnull=True)
                | Q(calculation_at__lt=F("updated_at"))
                | Q(force_calculation=True)
            )
        )

        return queryset


class PromotedContentResourceManager(
    models.Manager.from_queryset(PromotedContentResourceQueryset)
):
    """Manager for PromotedContentResource Model that uses (select|prefetch)_related."""

    def get_queryset(self):
        """Extend Queryset with (select|prefetch)_related."""
        from .models import ContentResource

        queryset = super().get_queryset()
        # Uses prefetch_related so that the ContentResource query
        # uses its (select|prefetch)_related methods.
        # This is specially important for Equivalence relations.
        # See: ContentResourceQueryset.get_prefetch_equivalences()
        queryset = queryset.select_related("resource")
        return queryset


class SubjectEquivalenceManager(models.Manager):
    """Manager to filter only subject equivalences."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(field="subject")


class CreatorEquivalenceManager(models.Manager):
    """Manager to filter only creator equivalences."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(field="creator")
