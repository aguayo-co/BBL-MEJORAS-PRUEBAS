from django.utils.translation import gettext_lazy as _
from import_export.fields import Field
from import_export.resources import ModelResource

from harvester.models import (
    CollectionAndResource,
    ContentResource,
    ContentResourceEquivalence,
    CreatorEquivalence,
    SubjectEquivalence,
)


class CollectionIEResource(ModelResource):
    collection_name = Field(
        attribute="collection__title", column_name=_("Nombre Colección"), readonly=True
    )
    description = Field(
        attribute="collection__description", column_name=_("Descripción"), readonly=True
    )
    owner = Field(column_name=_("Propietario"), readonly=True)
    resource_title = Field(
        attribute="resource__title", column_name=_("Título Recurso"), readonly=True
    )
    data_source = Field(
        attribute="resource__data_source__name", column_name=_("Fuente"), readonly=True
    )
    to_delete = Field(attribute="to_delete", column_name=_("Marcar para Borrado"))

    @staticmethod
    def dehydrate_owner(collection_and_resource):
        if hasattr(collection_and_resource, "collection"):
            return "[%s]: %s %s" % (
                collection_and_resource.collection.owner.username,
                collection_and_resource.collection.owner.first_name,
                collection_and_resource.collection.owner.last_name,
            )

    @staticmethod
    def dehydrate_resource_title(collection_and_resource):
        if hasattr(collection_and_resource, "resource"):
            return collection_and_resource.resource.processed_data.title

    class Meta:
        model = CollectionAndResource
        skip_unchanged = True
        report_skipped = True
        use_transactions = True
        use_bulk = True
        fields = (
            "id",
            "collection",
            "collection_name",
            "description",
            "owner",
            "resource",
            "resource_title",
            "data_source",
            "to_delete",
        )
        export_order = (
            "id",
            "collection",
            "collection_name",
            "description",
            "owner",
            "resource",
            "resource_title",
            "data_source",
            "to_delete",
        )
        import_id_fields = ("id",)


class ContentResourceIEResource(ModelResource):
    class Meta:
        model = ContentResource


class SubjectEquivalenceIEResource(ModelResource):
    field = Field(attribute="field", default="subject")

    class Meta:
        model = SubjectEquivalence
        skip_unchanged = True
        report_skipped = True
        use_transactions = True
        use_bulk = True
        exclude = (
            "created_at",
            "updated_at",
            "cite_type",
            "full_date",
            "icon_class",
        )
        export_order = [
            "id",
            "name",
            "wikidata_identifier",
            "id_bne",
            "id_unesco",
            "id_lcsh",
            "id_lembp",
            "priority",
            "field",
            "to_delete",
        ]


class CreatorEquivalenceIEResource(ModelResource):
    field = Field(attribute="field", default="creator")

    class Meta:
        model = CreatorEquivalence
        skip_unchanged = True
        report_skipped = True
        use_transactions = True
        use_bulk = True
        exclude = (
            "created_at",
            "updated_at",
            "cite_type",
            "full_date",
            "icon_class",
            "wikidata_identifier",
            "id_bne",
            "id_unesco",
            "id_lcsh",
            "id_lembp",
        )
        export_order = ["id", "name", "priority", "field", "to_delete"]


class ContentResourceEquivalenceIEResource(ModelResource):
    eq_name = Field(
        column_name="equivalence_name", attribute="equivalence__name", readonly=True
    )
    resources_count = Field(
        column_name="resources_count", attribute="resources_count_cached", readonly=True
    )

    class Meta:
        model = ContentResourceEquivalence
        skip_unchanged = True
        report_skipped = True
        use_transactions = True
        use_bulk = True
        exclude = (
            "created_at",
            "updated_at",
            "resources_count_cached",
            "resources_count_expiration",
            "resources_count_expired",
        )
        export_order = [
            "id",
            "original_value",
            "field",
            "equivalence",
            "eq_name",
            "resources_count",
            "to_delete",
        ]
