"""Api classes mixin."""
import datetime
import os
import datetime as dt

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from .forms.forms import CollectionAddToGroupsForm
from .models import (
    CollaborativeCollection,
    Collection,
    CollectionsGroup,
    CollectionsGroupCollection,
    ContentResource,
    Equivalence,
    SharedResource,
    SharedResourceUser,
)


class ProcessQueryParamsMixin:
    """Functions for query params processing."""

    def get_query_params(self, body):
        return {
            query_param.split("=")[0]: query_param.split("=")[1]
            for query_param in body.decode("utf-8").split("&")
        }


class ApiMixin:
    """Set Api default attributes and functions."""

    api = None
    api_paginatable_context = None
    api_http_method_names = ["get", "head"]

    def dispatch(self, request, *args, **kwargs):
        """Only accept get request for api."""
        if self.api:
            self.http_method_names = self.api_http_method_names

            try:
                return super().dispatch(request, *args, **kwargs)
            except Http404:
                return JsonResponse({}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def get_api_context_data(self, **kwargs):
        """Return context data for requested api."""
        return getattr(self, self.api)(**kwargs)

    def get_api_paginatable_response(
        self,
        reverse_url_name=None,
        reverse_url_args=None,
        results=None,
        **extra_response_args,
    ):
        """Return formatted paginatable response."""
        if reverse_url_name is None:
            reverse_url_name = self.api

        if reverse_url_args is None and hasattr(self, "object"):
            reverse_url_args = [self.object.pk]

        pagination = {"next": None, "previous": None}

        if self.api_paginatable_context["page_obj"].has_next():
            pagination["next"] = self.get_api_page_url(
                self.api_paginatable_context["page_obj"].next_page_number(),
                reverse_url_name,
                reverse_url_args,
            )
        if self.api_paginatable_context["page_obj"].has_previous():
            pagination["previous"] = self.get_api_page_url(
                self.api_paginatable_context["page_obj"].previous_page_number(),
                reverse_url_name,
                reverse_url_args,
            )

        if results is None:
            results = []

        return {
            "count": self.api_paginatable_context["page_obj"].paginator.count,
            "next": pagination["next"],
            "previous": pagination["previous"],
            "results": results,
            **extra_response_args,
        }

    def get_api_page_url(self, page_number, reverse_url_name, reverse_url_args=None):
        """Return an absolute page url."""
        params = self.request.GET.copy()
        params["page"] = page_number
        url = reverse(reverse_url_name, args=reverse_url_args)
        return url + "?" + params.urlencode()

    @staticmethod
    def get_user_info(user):
        """Return user's info attributes."""
        user_attributes = {
            "id": user.pk,
            "absolute_url": user.get_absolute_url(),
            "initials": user.initials,
            "full_name": user.full_name,
            "avatar": None,
            "country": user.country,
        }
        if hasattr(user, "profile") and user.profile.avatar:
            user_attributes["avatar"] = user.profile.avatar.url

        return user_attributes

    def get_api_content_resource_fields(self, content_resource):
        """Return content resource's attributes."""
        processed_data = content_resource.processed_data
        return {
            "id": content_resource.pk,
            "title": processed_data.title,
            "description": processed_data.description,
            "created_at": datetime.datetime.timestamp(processed_data.created_at),
            "updated_at": datetime.datetime.timestamp(processed_data.updated_at),
            "absolute_url": content_resource.get_absolute_url(),
            "api_absolute_url": reverse(
                "api_content_resource", args=[content_resource.pk]
            ),
            "image": processed_data.image,
            "creator": processed_data.creator,
            "publisher": processed_data.publisher,
            "publish_year": processed_data.date,
            "language": self.get_api_content_resource_equivalence(
                content_resource, "language"
            ),
            "data_source": self.get_api_contentresource_data_source(content_resource),
            "subjects": self.get_api_content_resource_equivalence(
                content_resource, "subject"
            ),
            "type": self.get_api_content_resource_equivalence(content_resource, "type"),
            "rights": self.get_api_content_resource_equivalence(
                content_resource, "rights"
            ),
            "is_exclusive": processed_data.is_exclusive,
            "citation": processed_data.citation,
            "format": processed_data.format,
            "coverage": processed_data.coverage,
        }

    @staticmethod
    def get_api_contentresource_data_source(content_resource):
        """Return the object's data source name and id."""
        return {
            "id": content_resource.processed_data.data_source.pk,
            "name": content_resource.processed_data.data_source.name,
        }

    @staticmethod
    def get_api_content_resource_equivalence(resource, field):
        """Return an object's equivalence name and id."""
        equivalences = []
        for content_resource_equivalence in getattr(resource, field).all():
            if content_resource_equivalence.equivalence:
                equivalence = {
                    "id": content_resource_equivalence.equivalence.pk,
                    "name": content_resource_equivalence.equivalence.name,
                }
                if field == "subject":
                    equivalences.append(equivalence)
                    continue
                return equivalence
        return equivalences if equivalences else None

    def get_api_collection_fields(self, collection):
        """Return collection's attributes."""
        collection_type = self.get_api_collection_type(collection)
        collection_fields = {
            "id": collection.pk,
            "type": collection_type,
            "title": collection.title,
            "description": collection.description,
            "created_at": datetime.datetime.timestamp(collection.created_at),
            "updated_at": datetime.datetime.timestamp(collection.updated_at),
            "absolute_url": collection.get_absolute_url(),
            "api_absolute_url": reverse("api_collection", args=[collection.pk]),
            "image": collection.image.url if collection.image else None,
            "resources_count": None,
            "owner": self.get_user_info(collection.owner),
            "subjects": None,
            "review_title": None,
            "review": None,
        }

        if collection.resources_by_type_count:
            collection_fields["resources_count"] = []
            for resource_type, count in collection.resources_by_type_count.items():
                collection_fields["resources_count"].append(
                    {"type": resource_type, "count": count}
                )

        return collection_fields

    @staticmethod
    def get_api_collection_type(collection):
        """Return the collection type."""
        if isinstance(collection, CollaborativeCollection):
            return CollaborativeCollection._meta.model_name

        return collection.get_subtype() or Collection._meta.model_name


class ApiSearchMixin(ApiMixin):
    """Return a search's results."""

    def api_search(self, context):
        """Return the context for search api requests."""
        self.api_paginatable_context = context

        return self.get_api_paginatable_response(
            results=[
                {**self.format_api_result(instance)}
                for instance in self.api_paginatable_context["object_list"] or []
            ],
            diyoumean=self.didyoumean,
        )

    def format_api_result(self, instance):
        """Return the resource fields data estructure."""
        if instance._meta.model_name is ContentResource._meta.model_name:
            content_resources_fields = self.get_api_content_resource_fields(instance)
            return content_resources_fields

        return self.get_api_collection_fields(instance)


class ApiSearchFiltersMixin(ApiMixin):
    """Return the available search's filters."""

    @staticmethod
    def api_search_filters():
        """Return the filters data estructure."""
        equivalences = list(
            Equivalence.objects.all().values_list("id", "name", "field")
        )
        filters = {"content_type": [], "subject": [], "rights": [], "language": []}
        for equivalence in equivalences:
            key = "content_type" if equivalence[2] == "type" else equivalence[2]
            filters[key].append({"id": equivalence[0], "name": equivalence[1]})
        return filters


class ApiContentResourceMixin(ApiMixin):
    """Content Resource Api functions."""

    def api_content_resource(self):
        """Return the content resource's attributes."""
        return self.get_api_content_resource_fields(self.object)

    def api_content_resource_reviews(self):
        """Return content resource reviews list."""
        self.paginatable_queryset = self.object.review_set.all()
        self.api_paginatable_context = self.get_context_data()

        return self.get_api_paginatable_response(
            results=[
                {
                    "author": self.get_user_info(review.author),
                    "rating": review.rating,
                    "text": review.text,
                }
                for review in self.api_paginatable_context["reviews"].all()
            ]
        )


class ApiCollectionDetailMixin(ApiMixin):
    """Collection Api Detail functions."""

    def api_collection(self):
        """Return the collection fields data estructure."""
        return self.get_api_collection_fields(self.object)

    def api_collection_collaborators(self):
        """Return collection collaborators list."""
        collection_type = self.get_api_collection_type(self.object)
        if collection_type == CollaborativeCollection._meta.model_name:
            self.paginated_objects_name = "collaborators"
            self.paginatable_queryset = (
                self.object.collaborativecollection.collaborators.filter(
                    collaborator__status=1
                )
            )
            self.api_paginatable_context = self.get_context_data()

            return self.get_api_paginatable_response(
                results=[
                    self.get_user_info(collaborator)
                    for collaborator in self.api_paginatable_context[
                        "collaborators"
                    ].all()
                ]
            )

        return self.get_api_paginatable_response()

    def api_collection_resources(self):
        """Return collection resources list."""
        self.paginatable_queryset = self.get_resources_queryset()
        self.api_paginatable_context = self.get_context_data()

        return self.get_api_paginatable_response(
            results=[
                self.get_api_content_resource_fields(resource)
                for resource in self.api_paginatable_context["resources"].all()
            ]
        )


class CollectionsGroupCollectionObjectView(SingleObjectMixin, View):
    def set_model_and_queryset_by_model_name(self, model_name, app_label="harvester"):
        self.model = apps.get_model(app_label=app_label, model_name=model_name)
        self.queryset = self.model.objects.visible()


class CollectionsGroupCollectionUpdateApiView(
    LoginRequiredMixin, ApiMixin, FormView, CollectionsGroupCollectionObjectView
):
    """Collections Group Collection Api."""

    http_method_names = ["post"]
    form_class = CollectionAddToGroupsForm

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        collection = self.get_object()
        users_groups = CollectionsGroup.objects.filter(
            owner=self.request.user
        ).values_list("pk", flat=True)
        return self.get_form_class().get_collections_groups_form_initial(
            collection, users_groups
        )

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.request.POST.get("form_prefix")

    def get_form_kwargs(self):
        """Pass the object instance to form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({"instance": self.get_object(), "user": self.request.user})
        return kwargs

    def post(self, request, *args, **kwargs):
        model_name = request.POST.get("model_name")
        self.set_model_and_queryset_by_model_name(model_name)
        return super().post(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        if cleaned_data["collections_groups"]:
            groups_names = ", ".join(
                cleaned_data["collections_groups"].values_list("title", flat=True)
            )
            return _(f"Has agregado esta colección a los grupos {groups_names}")
        return _("La colección ya no esta asignada a ningún grupo.")

    def form_valid(self, form):
        form.save()
        message = self.get_success_message(form.cleaned_data)
        return JsonResponse(
            {
                "message": message,
            }
        )


class CollectionsGroupCollectionFavoritesApiView(
    LoginRequiredMixin, ProcessQueryParamsMixin, CollectionsGroupCollectionObjectView
):
    """Collections Favorites Group Api."""

    http_method_names = ["post", "delete"]

    def post(self, request, *args, **kwargs):
        model_name = request.POST.get("model_name")
        self.set_model_and_queryset_by_model_name(model_name)
        CollectionsGroupCollection.add_to_favorites(
            self.get_object(), self.request.user
        )
        return JsonResponse({"message": _("Colección agregada a favoritos.")})

    def delete(self, request, *args, **kwargs):
        body = self.get_query_params(request.body)
        self.set_model_and_queryset_by_model_name(body["model_name"])
        result = CollectionsGroupCollection.remove_from_favorites(
            self.get_object(), self.request.user
        )
        if result[0]:
            return JsonResponse({"message": _("Colección eliminada de tus favoritos.")})
        return JsonResponse(
            {"message": _("La colección no pudo ser eliminada de tus favoritos.")},
            status=500,
        )


class SharedResourcesApiView(LoginRequiredMixin, SingleObjectMixin, View):
    """Shared Resources Actions Api."""

    model = SharedResourceUser
    queryset = model.objects.prefetch_related(
        Prefetch(
            "shared_resource",
            queryset=SharedResource.objects.select_related("owner")
            .select_related("resource")
            .all(),
        )
    )
    http_method_names = ["post"]

    def ignore(self, notification, user):
        if (
            notification.user == user
            and notification.status == notification.SHARED_RESOURCE_STATUS_CHOICES[0][0]
        ):
            notification.status = notification.SHARED_RESOURCE_STATUS_CHOICES[2][0]
            notification.save()
            return JsonResponse({"message": _("Recurso compartido ignorado.")})
        if (
            notification.user != user
            or notification.status != notification.SHARED_RESOURCE_STATUS_CHOICES[0][0]
        ):
            return JsonResponse(
                {"message": _("El recurso compartido no pudo ser ignorado.")},
                status=400,
            )

    def post(self, request, *args, **kwargs):
        notification = self.get_object()
        user = self.request.user
        if "method" in kwargs:
            return getattr(self, kwargs["method"])(notification, user)
        return JsonResponse(
            {"message": _("Debes enviar un método en la url.")},
            status=400,
        )


class ValidateFileApiView(LoginRequiredMixin, SingleObjectMixin, View):
    """Shared Resources Actions Api."""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        lessOneHour = dt.datetime.now() - dt.timedelta(hours=0, minutes=30)
        path = "/tmp/"
        files = os.listdir(path)
        filesIn = []
        for file in files:
            filetime = dt.datetime.fromtimestamp(os.path.getctime(path + file))
            if filetime > lessOneHour:
                filesIn.append(file)

        return JsonResponse(
            {"count": len(filesIn)},
            status=200,
        )
