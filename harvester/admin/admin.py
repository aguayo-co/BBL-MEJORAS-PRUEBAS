"""Define admin interfaces for Harvester app."""

from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ExportActionMixin, ImportExportActionModelAdmin
from import_export.fields import Field
from simple_history.admin import SimpleHistoryAdmin

from resources.helpers import get_resolved_referer
from ..common import DUBLIN_CORE_DEFAULT_ASSOCIATION_INITIAL

from ..models import (
    AdminNotification,
    CollaborativeCollection,
    Collaborator,
    Collection,
    CollectionAndResource,
    CollectionsGroup,
    ContentResource,
    CreatorEquivalence,
    Equivalence,
    PromotedContentResource,
    Review,
    Set,
    SubjectEquivalence,
)
from .actions import (
    hide,
    mark_for_delete_in_background,
    set_home_internal,
    set_home_site,
    show,
    unset_home_internal,
    unset_home_site,
    mass_change_resource_set,
)
from .filters import EquivalenceMappingFilter
from .import_export_resources import (
    CollectionIEResource,
    ContentResourceIEResource,
    CreatorEquivalenceIEResource,
    SubjectEquivalenceIEResource,
)
from .mixins import ExportInBackgroundMixin


class AdminNotificationResource(resources.ModelResource):

    created_at = Field(attribute="created_at", column_name=_("Fecha de creación"))
    notification_object_type = Field(column_name=_("Tipo de notificación"))
    notification_object_title = Field(column_name=_("Nombre"))
    notification_object_text = Field(column_name=_("Text0"))
    notification_object_description = Field(column_name=_("Descripción"))
    notification_object_author = Field(column_name=_("Autor"))
    notification_object_owner = Field(column_name=_("Dueño"))
    notification_object_visible = Field(column_name=_("Visible"))
    notification_object_resources_count = Field(
        column_name=_("Cantidad de recursos asociados")
    )

    class Meta:

        model = AdminNotification
        fields = [
            "created_at",
            "notification_object_type",
            "notification_object_title",
            "notification_object_author",
            "notification_object_owner",
            "notification_object_visible",
            "notification_object_resources_count",
        ]

    def dehydrate_notification_object_type(self, obj):
        return obj.content_type

    def dehydrate_notification_object_title(self, obj):
        return obj.content_object.title

    def dehydrate_notification_object_text(self, obj):
        return obj.get_notification_object_field("text")

    def dehydrate_notification_object_description(self, obj):
        return obj.get_notification_object_field("description")

    def dehydrate_notification_object_author(self, obj):
        return obj.get_notification_object_field("author")

    def dehydrate_notification_object_owner(self, obj):
        return obj.get_notification_object_field("owner")

    def dehydrate_notification_object_visible(self, obj):
        return obj.get_notification_object_field("visible")

    def dehydrate_notification_object_resources_count(self, obj):
        return obj.get_notification_object_field("resources_count")


class AdminNotificationTypeFilter(SimpleListFilter):

    title = _("Tipo de notificación")
    parameter_name = "notification_type"

    def lookups(self, request, model_admin):
        return (
            ("review", _("Reseña")),
            ("collection", _("Colección")),
            ("collaborativecollection", _("Colección Colaborativa")),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == "review":
            content_type = ContentType.objects.get_for_model(Review)
            return queryset.filter(content_type=content_type)
        if self.value().lower() == "collection":
            content_type = ContentType.objects.get_for_model(Collection)
            return queryset.filter(content_type=content_type)
        if self.value().lower() == "collaborativecollection":
            content_type = ContentType.objects.get_for_model(CollaborativeCollection)
            return queryset.filter(content_type=content_type)


@admin.register(AdminNotification)
class AdminNotificationAdmin(
    ExportInBackgroundMixin, ExportActionMixin, admin.ModelAdmin
):
    """Admin notifications in django admin."""

    resource_class = AdminNotificationResource

    list_display_links = None
    list_display = [
        "created_at",
        "content_type",
        "object_title",
        "object_author",
        "object_owner",
        "object_visible",
        "object_resources_count",
    ]
    list_filter = [AdminNotificationTypeFilter, ("created_at", DateFieldListFilter)]
    sortable_by = ("created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions_to_delete = ["mark_for_delete_in_background", "delete_selected"]
        for action in actions_to_delete:
            if action in actions:
                del actions[action]
        return actions

    def content_type(self, obj):
        return obj.content_type

    content_type.short_description = _("Tipo de notificación")

    def object_title(self, obj):
        print(obj)
        return obj.content_object.title

    object_title.short_description = _("Nombre")

    def object_author(self, obj):
        return obj.get_notification_object_field("author")

    object_author.short_description = _("Autor")

    def object_owner(self, obj):
        return obj.get_notification_object_field("owner")

    object_owner.short_description = _("Dueño")

    def object_visible(self, obj):
        return obj.get_notification_object_field("visible")

    object_visible.short_description = _("Visible")

    def object_resources_count(self, obj):
        return obj.get_notification_object_field("resources_count")

    object_resources_count.short_description = _("Cantidad de recursos asociados")


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    """Integrate Set with DJango admin."""

    actions = [
        hide,
        show,
        set_home_site,
        unset_home_site,
        set_home_internal,
        unset_home_internal,
    ]
    list_display = [
        "name",
        "data_source",
        "resources__count",
        "visible",
        "home_site",
        "home_internal",
        "updated_at",
        "created_at",
    ]
    list_filter = ["updated_at", "visible", "data_source", "data_source__exclusive"]
    search_fields = ["name"]
    readonly_fields = ["spec", "data_source"]
    exclude = ("to_delete",)

    def resources__count(self, obj):
        """Return content_resource count."""
        return obj.resources_count

    resources__count.short_description = _("Número de Recursos")
    resources__count.admin_order_field = "resources_count_cached"

    def has_add_permission(self, request):
        """
        Disallow add.

        Sets are only created when harvesting.
        """
        return False


@admin.register(ContentResource)
class ContentResourceAdmin(
    AdminAdvancedFiltersMixin,
    ExportInBackgroundMixin,
    ExportActionMixin,
    admin.ModelAdmin,
):
    """Integrate ContentResource with Django admin."""

    actions = [hide, show, mass_change_resource_set]
    list_display = [
        "title",
        "creator_equivalence",
        "data_source",
        "visible",
        "collection__count",
        "updated_at",
        "created_at",
    ]
    list_filter = [
        EquivalenceMappingFilter,
        "updated_at",
        "visible",
        "sets"
    ]
    readonly_fields = ContentResource.FIELDS_WITH_EQUIVALENCES
    search_fields = [
        "title__0__icontains",
    ]
    exclude = ("to_delete",)
    resource_class = ContentResourceIEResource
    fieldsets = [
        (
            "Atributos DublinCore",
            {
                "fields": [
                    field for field in DUBLIN_CORE_DEFAULT_ASSOCIATION_INITIAL.values()
                ]
            },
        ),
        ("Campos Calculados", {"fields": ["dynamic_identifier_cached"]}),
    ]
    advanced_filter_fields = (
        ("data_source__name", "Fuente"),
        ("sets__name", "Colección Institucional"),
        ("description", "Descripción (Original)"),
        (
            "creatorequivalencerelation__contentresourceequivalence__equivalence__name",
            "Autor (Equivalencia)",
        ),
        (
            "creator__original_value",
            "Autor (Original)",
        ),
        (
            "subjectequivalencerelation__contentresourceequivalence__equivalence__name",
            "Tema (Equivalencia)",
        ),
        (
            "subject__original_value",
            "Tema (Original)",
        ),
    )

    def has_add_permission(self, request):
        """
        Disallow add.

        Resources are only created when harvesting.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Disallow change.

        Resources are only updateing when harvesting.
        """
        return False

    def has_delete_in_background_permission(self, request, obj=None):
        """Check if current user has permission for background deletion."""
        return request.user.has_perm("harvester.delete_in_background")

    def get_search_results(self, request, queryset, search_term):
        """
        Return search results limited depending on the REFERER.

        This override the default implementation to use a single lookup per
        search_field. The search_field should include the full lookup,
        example: `title__icontains`

        If the request comes from a PromotedContentResource admin page,
        limit queryset with the `limit_choices_to` option of the `resource` field.
        """
        use_distinct = False

        if search_term:
            search_term = search_term.strip()

        if not search_term or len(search_term) < 4:
            return queryset, use_distinct

        referer = get_resolved_referer(request)
        if referer and referer.url_name.startswith("harvester_promotedcontentresource"):
            queryset = queryset.filter(**PromotedContentResource.RESOURCE_FILTERS)

        or_filters = Q()
        for search_field in self.search_fields:
            or_filters |= Q(**{search_field: search_term})
        return queryset.filter(or_filters), use_distinct

    def collection__count(self, obj):
        """Return count of Collections this Resource belongs to."""
        return obj.collection_count

    def creator_equivalence(self, obj):
        return obj.creator.first()

    collection__count.short_description = _("Número de colecciones")
    collection__count.admin_order_field = "collection_count_cached"


@admin.register(PromotedContentResource)
class PromotedContentResourceAdmin(SimpleHistoryAdmin):
    """Define admin integration for PromotedContentResource model."""

    autocomplete_fields = ["resource"]
    list_display = ["resource", "priority", "updated_at", "created_at"]
    exclude = ("to_delete",)

    def get_readonly_fields(self, request, obj=None):
        """
        Return readonly fields.

        If the obj has a PK, the resource is readonly.
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.pk:
            readonly_fields = (*readonly_fields, "resource")
        return readonly_fields


@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin):
    """Define admin integration for Review model."""

    autocomplete_fields = ["resource", "author"]
    list_display = ["resource", "rating", "author", "updated_at", "created_at"]
    list_filter = ["resource__sets", "resource__data_source", "rating"]
    exclude = ("to_delete",)


class CollectionAndResourceInline(admin.TabularInline):
    """Inline to associate ContentResources to Collections."""

    model = CollectionAndResource

    autocomplete_fields = ["resource"]
    exclude = ("to_delete",)


class CollectionAdminBase(
    ExportInBackgroundMixin, ImportExportActionModelAdmin, SimpleHistoryAdmin
):
    """Define base admin integration for Collection based models."""

    actions = [
        hide,
        show,
        set_home_site,
        unset_home_site,
        set_home_internal,
        unset_home_internal,
        "export_admin_action",
    ]
    autocomplete_fields = ["owner"]
    inlines = [CollectionAndResourceInline]
    list_display = [
        "title",
        "owner",
        "visible",
        "resources__count",
        "home_site",
        "home_internal",
        "updated_at",
        "created_at",
    ]
    list_filter = ["visible"]
    search_fields = ["title"]
    readonly_fields = ["detail_image"]
    exclude = ("to_delete",)
    resource_class = CollectionIEResource

    def resources__count(self, obj):
        """Return resources count for an object."""
        return obj.resources_count

    def get_custom_export_queryset(self, queryset):
        return self.resource_class._meta.model.objects.filter(collection__in=queryset)

    resources__count.short_description = _("Número de recursos")
    resources__count.admin_order_field = "resources_count_cached"


@admin.register(Collection)
class CollectionAdmin(CollectionAdminBase):
    """Define admin integration for Collection model."""

    def get_queryset(self, request):
        """Filter queryset to exclude subclasses."""
        return super().get_queryset(request).exclude_subclasses()


class CollaboratorInline(admin.TabularInline):
    """Inline to associate ContentResources to Collections."""

    model = Collaborator

    autocomplete_fields = ["user"]
    extra = 3
    exclude = ("to_delete",)


@admin.register(CollaborativeCollection)
class CollaborativeCollectionAdmin(CollectionAdminBase):
    """Define admin integration for CollaborativeCollection model."""

    inlines = CollectionAdminBase.inlines + [CollaboratorInline]


class EquivalenceFieldFilter(admin.SimpleListFilter):
    """Custom Filter for Equivalence, remove separated modules."""

    title = _("Tipo Equivalencia")
    parameter_name = "type"

    def lookups(self, request, model_admin):
        """Customize available options for filter."""
        return (
            ("type", _("tipo de contenido")),
            ("language", _("idioma")),
            ("rights", _("derechos")),
        )

    def queryset(self, request, queryset):
        """Apply filters to the queryset."""
        if self.value():
            return queryset.filter(field=self.value())


@admin.register(Equivalence)
class EquivalenceAdmin(admin.ModelAdmin):
    """Define admin integration for Equivalences model."""

    list_display = ["name", "field", "updated_at", "created_at"]
    list_filter = [EquivalenceFieldFilter]
    search_fields = ["name"]
    exclude = ("to_delete",)

    def get_exclude(self, request, obj=None):
        """Hide `icon_class` if not a `type` :model:`harvester.Equivalence`."""
        exclude = list(super().get_exclude(request, obj) or [])
        if obj and obj.id and obj.field != "type":
            exclude.extend(["icon_class", "full_date"])
        exclude.extend(
            [
                "id_bne",
                "id_lcsh",
                "id_lembp",
                "id_lembp",
                "wikidata_identifier",
                "id_unesco",
            ]
        )
        return exclude

    def get_readonly_fields(self, request, obj=None):
        """Make `field` read_only for existing :model:`harvester.Equivalence`."""
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.id:
            readonly_fields = readonly_fields or []
            readonly_fields.append("field")
        return readonly_fields

    def get_queryset(self, request):
        """Hide separated equivalences modules."""
        qs = super().get_queryset(request)
        return qs.exclude(field__in=["subject", "creator"])


@admin.register(SubjectEquivalence)
class SubjectEquivalenceAdmin(
    ExportInBackgroundMixin, ImportExportActionModelAdmin, admin.ModelAdmin
):
    """Separated Equivalences for Subject Field."""

    list_filter = ["updated_at", "created_at"]
    resource_class = SubjectEquivalenceIEResource

    def get_changeform_initial_data(self, request):
        """Set Initial value for fields."""
        initial = super().get_changeform_initial_data(request)
        initial.update({"field": "subject"})
        return initial

    def get_readonly_fields(self, request, obj=None):
        """Make `field` read_only for existing :model:`harvester.Equivalence`."""
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.id:
            readonly_fields = readonly_fields or []
            readonly_fields.append("field")
        return readonly_fields

    def get_exclude(self, request, obj=None):
        """Hide `icon_class` if not a `type` :model:`harvester.Equivalence`."""
        exclude = list(super().get_exclude(request, obj) or [])
        if obj and obj.id and obj.field != "type":
            exclude.extend(["icon_class", "full_date"])
        exclude.extend(["icon_class", "full_date", "cite_type"])
        return exclude


@admin.register(CreatorEquivalence)
class CreatorEquivalenceAdmin(
    ExportInBackgroundMixin, ImportExportActionModelAdmin, admin.ModelAdmin
):
    """Separated Equivalences for Creator Field."""

    list_filter = ["updated_at", "created_at"]
    resource_class = CreatorEquivalenceIEResource

    def get_changeform_initial_data(self, request):
        """Set Initial value for fields."""
        initial = super().get_changeform_initial_data(request)
        initial.update({"field": "creator"})
        return initial

    def get_readonly_fields(self, request, obj=None):
        """Make `field` read_only for existing :model:`harvester.Equivalence`."""
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.id:
            readonly_fields = readonly_fields or []
            readonly_fields.append("field")
        return readonly_fields

    def get_exclude(self, request, obj=None):
        """Hide `icon_class` if not a `type` :model:`harvester.Equivalence`."""
        exclude = list(super().get_exclude(request, obj) or [])
        if obj and obj.id and obj.field != "type":
            exclude.extend(["icon_class", "full_date"])
        exclude.extend(
            [
                "icon_class",
                "full_date",
                "cite_type",
                "id_bne",
                "id_lcsh",
                "id_lembp",
                "id_lembp",
                "wikidata_identifier",
                "id_unesco",
            ]
        )
        return exclude


@admin.register(CollectionsGroup)
class CollectionsGroupAdmin(admin.ModelAdmin):
    """Define admin integration for Equivalences model."""

    autocomplete_fields = ["owner"]

    list_display = [
        "title",
        "owner",
        "collections",
        "updated_at",
        "created_at",
        "collections__count",
    ]
    search_fields = ["title", "owner__first_name", "owner__last_name"]

    def collections__count(self, obj):
        """Return resources count for an object."""
        return obj.collections_count


# Site Wide Actions
admin.site.add_action(mark_for_delete_in_background, "mark_for_delete_in_background")
