"""Define views for harvester app."""

import logging

from constance import config
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    AccessMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch, Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.detail import (
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
)
from django.views.generic.edit import (
    CreateView,
    FormView,
    ModelFormMixin,
    ProcessFormView,
    UpdateView,
)

from harvester.models.helpers import ContentResourceProcessor
from hitcount.views import HitCountDetailView
from resources.helpers import get_resolved_referer
from resources.views import (
    CachedObjectMixin,
    CollectionInMultiformMixin,
    CollectionsGroupsFormsetMixin,
    FilteringMixin,
    MultiFormsMixin,
    MultiFormSuccessMessageMixin,
    OrderingMixin,
    PaginatorMixin,
)
from search_engine.forms import (
    SearchFormWithCollectionFilterMixin,
    SearchFormWithSetFilterMixin,
)

from .forms import forms
from .forms.forms import COLLECTION_TYPE_CHOICES, ReviewActionsForm, ReviewForm
from .models import (
    CollaborativeCollection,
    Collection,
    CollectionsGroup,
    CollectionsGroupCollection,
    ContentResource,
    ContentType,
    DataSource,
    DynamicIdentifierConfig,
    Review,
    Set,
    SharedResource,
    SharedResourceUser,
)
from .views_api import (
    ApiCollectionDetailMixin,
    ApiContentResourceMixin,
    ProcessQueryParamsMixin,
)

from django.conf import settings

ROBOTS_ALLOW_HOST_SETTING = "ROBOTS_ALLOW_HOST"
ROBOTS_ALLOW_TEMPLATE = "robots.txt"
ROBOTS_DISALLOW_TEMPLATE = "robots-disallow.txt"

bbl_logger = logging.getLogger("biblored")  # pylint: disable=invalid-name


class GoBackUrlMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if "next" in self.request.GET:
            context["go_back_url"] = self.request.GET["next"]
        return context


class CancellShareMessageMixin:
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.
        If content resource sharing is cancelled shows a message.
        """
        if "cancelled" in request.GET:
            messages.success(self.request, _("No compartiste ningún recurso."))
            return HttpResponseRedirect(request.build_absolute_uri(request.path))
        return super().get(request, *args, **kwargs)


class reviewFormActionsMixin(FormView):
    form_class = ReviewActionsForm

    def get_form_kwargs(self):
        """Pass the object instance to form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        form.save()
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_message(self, cleaned_data):
        """Show a message when post is successful."""
        if cleaned_data["remove_review"]:
            return _("Se ha eliminado la reseña")

        return None


class BaseUserSearchSelectFormViewMixin(
    LoginRequiredMixin,
    CachedObjectMixin,
    SuccessMessageMixin,
    FormView,
    SingleObjectMixin,
):
    """Update Collaborators for Collections."""

    raise_exception = True
    template_name = None
    form_class = None
    success_message = None
    model = None

    def get_form_kwargs(self):
        """Pass the object instance to form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["object"] = self.object
        form_kwargs["request"] = self.request
        return form_kwargs

    def form_valid(self, form):
        """Call form save."""
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return to the object detail page."""
        if "next" in self.request.GET:
            return f'{self.request.GET["next"]}#{self.object.pk}'
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        """Instance the object and continue post."""
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Check if a query param is present and return the correct get response."""
        self.object = self.get_object()
        if "search_text" in request.GET:
            return self.render_users_autocomplete()
        return super().get(request, *args, **kwargs)

    def render_users_autocomplete(self):
        """Return a list of valid users."""
        search_text = self.request.GET.get("search_text")
        User = get_user_model()
        results_queryset = User.objects.search(search_text)[:20]
        response = User.format_search_users_result_queryset(
            results_queryset, search_text
        )
        return JsonResponse(response)


class ContentResourceDetailView(
    CancellShareMessageMixin,
    ApiContentResourceMixin,
    AccessMixin,
    PaginatorMixin,
    reviewFormActionsMixin,
    HitCountDetailView,
):
    """Show details of a Content Resource."""

    model = ContentResource
    queryset = model.objects.visible()
    count_hit = False
    paginated_objects_name = "reviews"
    paginate_by = 4
    review_permissions = ["harvester.add_review"]
    object = None

    def get_object(self, queryset=None):
        """
        Return the object instance for the current resource.

        The instance will have the ez-proxy user to generate valid links
        and related for the current logged in user.
        """
        resource = super().get_object(queryset)
        if self.request.user.is_authenticated:
            resource.related.related_for_user = self.request.user
        return resource

    def dispatch(self, request, *args, **kwargs):
        """Enable hit_count if user is authenticated."""
        if self.request.user.is_authenticated:
            self.count_hit = True
        return super().dispatch(request, *args, **kwargs)

    def log_external_resource_redirect(self, user, url):
        """Write to the log that a user was sent to a resource's external URL."""
        msg = "ha sido redirigido a la url externa del recurso %(resource_id)s: %(url)s [%(datasource)s]"  # noqa: E501
        args = {
            "resource_id": self.object.id,
            "url": url,
            "datasource": self.object.data_source.name,
        }

        if user.is_authenticated:
            msg = "El Usuario %(user_id)s (%(username)s) " + msg
            args.update({"user_id": user.id, "username": user.username})
        else:
            msg = "Un usuario anónimo " + msg

        bbl_logger.info(msg, args)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.

        Returns Rest API response if requested.
        Redirects to external url if requested.
        Initialize the Review form if not created yet.
        Render object page.
        """
        if "notification" in self.request.GET:
            try:
                SharedResourceUser.objects.get(
                    pk=self.request.GET["notification"]
                ).mark_as_read(self.request.user)
            except SharedResourceUser.DoesNotExist:
                pass

        self.object = self.get_object()

        if self.api:
            return JsonResponse(self.get_api_context_data())

        if "external" in request.GET:
            url_data = self.object.processed_data.url_processor(request.user)
            if url_data:
                url, external = url_data
                if external:
                    self.log_external_resource_redirect(request.user, url)
                return HttpResponseRedirect(url)

        self.paginatable_queryset = self.object.review_set.all()

        return super().get(request, *args, **kwargs)

    def get_referer_exposition(self):
        """Get the referer exposition for this view if there is one."""
        referer = get_resolved_referer(self.request)
        if not referer or referer.app_name != "expositions":
            return None

        path_components = [
            component for component in referer.args[0].split("/") if component
        ]
        try:
            page, __, ___ = self.request.site.root_page.specific.route(
                self.request, path_components
            )
        except Http404:
            return None

        if page.content_type.model == "homepage":
            return None

        return page

    def get_context_data(self, **context):
        """Extend context for ContentResource detail view."""
        context["referer_exposition"] = self.get_referer_exposition()
        context["user_has_review_permissions"] = self.request.user.has_perms(
            self.review_permissions
        )
        return super().get_context_data(**context)

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class CollectionDetailView(
    CancellShareMessageMixin,
    SearchFormWithCollectionFilterMixin,
    CollectionInMultiformMixin,
    ApiCollectionDetailMixin,
    UserPassesTestMixin,
    FilteringMixin,
    OrderingMixin,
    PaginatorMixin,
    MultiFormSuccessMessageMixin,
    MultiFormsMixin,
    DetailView,
):
    """Show details of a Collection."""

    model = Collection
    queryset = (
        model.objects.visible()
        .prefetch_related("collaborativecollection")
        .annotate_groups()
    )

    paginated_objects_name = "resources"
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title__0"]),
        "za": (_("De la Z a la A"), ["-title__0"]),
        "recent": (_("Más reciente"), ["-calculated_date"]),
        "-recent": (_("Menos reciente"), ["calculated_date"]),
    }
    filters_form_class = forms.ContentResourceFilters

    form_classes = {
        "content_resources_actions": forms.ContentResourceActionsForm,
    }

    template_name = "harvester/collection_detail.html"

    def get_success_url(self, form_name=None):
        if form_name == "content_resources_actions":
            return self.request.get_full_path()
        return super().get_success_url(form_name)

    def get_forms(self, form_classes):
        """Return instances of the form for authenticated users."""
        if self.request.user.is_anonymous:
            return None
        return super().get_forms(form_classes)

    def test_func(self):
        """Only allow POST to owner of the collection."""
        if self.request.method.lower() == "post":
            if self.request.user.is_anonymous:
                return False

            if self.request.POST.get("remove_resource", None):
                return self.request.user == self.get_object().owner

        return True

    def get_resources_queryset(self):
        """Return the queryset for the collection resources."""
        return self.filter_queryset(
            self.order_queryset(self.object.resources.visible())
        )

    def get(self, request, *args, **kwargs):
        """
        Handle GET request.
        Set a paginatable resources queryset.
        """
        self.object = self.get_object()

        if self.api:
            return JsonResponse(self.get_api_context_data())

        self.paginatable_queryset = self.get_resources_queryset()

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request.

        Set a paginatable resources queryset and proceed with form processing.
        """
        self.object = self.get_object()
        self.paginatable_queryset = self.get_resources_queryset()
        return super().post(request, *args, **kwargs)

    def get_content_resources_actions_form_extra_kwargs(self):
        """Pass the object instance to form."""
        collection = self.get_object()
        user = self.request.user
        return {"collection": collection, "user": user}

    def content_resources_actions_form_valid(self, form, form_name):
        """Save form (remove resource) and redirect to success url."""
        form.save()
        return HttpResponseRedirect(self.get_success_url(form_name))

    def collection_form_valid(self, form, form_name):
        """Save collection form and redirect to success url."""
        super().collection_form_valid(form, form_name)
        return HttpResponseRedirect(self.get_success_url(form_name))

    def content_resources_actions_form_invalid(self, forms):
        """Present error message, and re-render page."""
        messages.error(
            self.request,
            _("No pudimos eliminar el recurso de la colección. Intenta nuevamente."),
        )
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_success_message(self, cleaned_data, form_name=None):
        """Show a message when post is successful."""
        if form_name == "content_resources_actions":
            if cleaned_data["remove_resource"]:
                return _("Se ha eliminado el recurso de la colección")

            if "collaborate" in cleaned_data:
                if cleaned_data["collaborate"]:
                    return _("Solicitud para colaborar enviada")
                return _("Has dejado de colaborar en esta colección")

        return super().get_success_message(cleaned_data, form_name)


class CollectionsGroupDetailView(
    CancellShareMessageMixin,
    LoginRequiredMixin,
    CollectionsGroupsFormsetMixin,
    UserPassesTestMixin,
    OrderingMixin,
    PaginatorMixin,
    SuccessMessageMixin,
    FormView,
    DetailView,
):
    """Show details of a Collections group."""

    model = CollectionsGroup

    form_class = forms.CollectionActionsForm

    paginated_objects_name = "collections"
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-created_at"]),
        "-recent": (_("Menos reciente"), ["created_at"]),
    }
    filters_form_class = forms.ContentResourceFilters
    favorites = False
    favorites_group = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.favorites_group = CollectionsGroup.objects.get_or_create(
            title="favoritos", owner=self.request.user
        )[0]

    def get_form(self, form_class=None):
        """Return an instance of the form for authenticated users."""
        if self.request.user.is_anonymous:
            return None

        return super().get_form(form_class)

    def test_func(self):
        """Only allow to owner to interacts with the collections group."""
        return self.request.user == self.get_object().owner

    def get_queryset(self):
        """Filter queryset only with the ones owned by the request's user."""
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)

    def get_collections_queryset(self):
        """Return the queryset for the group collection collections."""

        collections_groups_collection = CollectionsGroupCollection.objects.filter(
            collections_group=self.get_object(),
        )

        return self.order_mixed_queryset(collections_groups_collection)

    def get(self, request, *args, **kwargs):
        """
        Handle GET request.

        Set a paginatable collections queryset.
        """
        self.object = self.get_object()
        self.paginatable_queryset = self.get_collections_queryset()
        self.collections_formset_object_list = self.paginatable_queryset
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request.

        Set a paginatable resources queryset and proceed with form processing.
        """
        self.object = self.get_object()
        self.paginatable_queryset = self.get_collections_queryset()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pass the object instance to form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["collections_group"] = self.get_object()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_object(self, queryset=None):
        """Verify is favorites is requested."""
        if self.favorites:
            return self.favorites_group
        return super().get_object()

    def form_valid(self, form):
        """Save form (remove resource) and redirect to success url."""
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """Present error message, and re-render page."""
        messages.error(
            self.request,
            _("No pudimos eliminar la colección del grupo. Intenta nuevamente."),
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Return to the same URL we are in, including query params.

        This is required so the user does not looses pagination or sorting options.
        """
        return self.request.get_full_path()

    def get_success_message(self, cleaned_data):
        """Show a message when post is successful."""
        if cleaned_data["remove_collection"]:
            return _("Se ha eliminado la colección del grupo")

        return None


class ContentResourceCollectionsFormView(
    LoginRequiredMixin, SuccessMessageMixin, UpdateView
):
    """Update associations of a ContentResource to Collections."""

    raise_exception = True
    template_name = "harvester/contentresourcecollections_form.html"
    form_class = forms.ContentResourceCollectionsForm
    model = ContentResource
    success_message = _("Colecciones guardadas correctamente.")

    def get_form_kwargs(self):
        """Set Logged in user as parameter to form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        """Return the same url with a done param at the end."""
        url = reverse(
            self.request.resolver_match.url_name,
            args=self.request.resolver_match.args,
            kwargs=self.request.resolver_match.kwargs,
        )
        return f"{url}?done"

    def get_context_data(self, **kwargs):
        """Do not include form if `done` is in the url."""
        if "done" in self.request.GET:
            kwargs["form"] = None
        return super().get_context_data(**kwargs)


class ShareContentResourceFormView(BaseUserSearchSelectFormViewMixin):
    """Share a Content Resource with users or through social networks."""

    raise_exception = True
    template_name = "harvester/share_content_resource_form.html"
    form_class = forms.ShareContentResourceForm
    success_message = _("Contenido compartido.")
    model = ContentResource

    def render_users_autocomplete(self):
        """Return a list of users valid for Collaborate."""
        search_text = self.request.GET.get("search_text")
        try:
            shared_resource = SharedResource.objects.get(
                owner=self.request.user, resource=self.get_object()
            )
        except SharedResource.DoesNotExist:
            shared_resource = None
        users_queryset = self.get_form_class().get_valid_users_queryset(
            self.request.user, time_filter=False
        )
        User = get_user_model()
        results_queryset = users_queryset.search(search_text)[:20]
        response = User.format_search_users_result_queryset(
            results_queryset,
            search_text,
            extra_keys=["shared_date"],
            shared_resource=shared_resource,
        )
        return JsonResponse(response)


class CollectionAddView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create New Collections."""

    template_name = "harvester/collection_form.html"
    form_class = forms.CollectionForm
    success_message = _("Colección creada correctamente.")

    def form_valid(self, form):
        """
        Process successful form submissions.

        It saves de form, and adds Resource to the collection if one is
        received in the URL.
        """
        response = super().form_valid(form)
        self.process_resource_from_url()
        return response

    def process_resource_from_url(self):
        """
        Add the resource from the url to the Collection.

        If the ID is not valid, nothing will happen.
        """
        if "resource" in self.request.GET:
            try:
                resource_id = int(self.request.GET["resource"])
            except ValueError:
                return

            try:
                resource = ContentResource.objects.get(pk=resource_id)
            except ContentResource.DoesNotExist:
                return

            self.object.resources.add(resource)

    def get_form_kwargs(self):
        """Check if is a Collaborative  Collection and pass the instance."""
        form_kwargs = super().get_form_kwargs()
        is_collaborative = self.request.POST.get("collaborative", False)
        object_class = CollaborativeCollection if is_collaborative else Collection
        form_kwargs["instance"] = object_class(owner=self.request.user)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())


class CollectionsGroupAddView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create New Collections."""

    template_name = "harvester/collectionsgroup_form.html"
    form_class = forms.CollectionsGroupForm
    success_message = _("Grupo de colecciones creado correctamente.")

    def form_valid(self, form):
        """
        Process successful form submissions.

        It saves de form, and adds Resource to the collection if one is
        received in the URL.
        """
        response = super().form_valid(form)
        self.process_collection_from_url()
        return response

    def process_collection_from_url(self):
        """
        Add the collection from the url to the Collections Group.

        If the ID is not valid, nothing will happen.
        """
        if "collection" in self.request.GET:
            try:
                collection_id = int(self.request.GET["collection"])
            except ValueError:
                return

            try:
                collection = Collection.objects.get(pk=collection_id)
            except Collection.DoesNotExist:
                return

            self.object.collections.add(collection)

    def get_form_kwargs(self):
        """Check if is a Collaborative  Collection and pass the instance."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["instance"] = CollectionsGroup(owner=self.request.user)
        return form_kwargs


class CollectionEditView(
    CachedObjectMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Edit an existent Collection."""

    raise_exception = True
    template_name = "harvester/collection_form.html"
    success_message = _("Colección modificada correctamente.")
    queryset = Collection.objects.all()

    def test_func(self):
        """Only allow access to owner of the collaborative_collection."""
        return self.request.user == self.get_object().owner

    def get_form_class(self):
        """Check if is a Collaborative  Collection and pass the form class."""
        if isinstance(self.object, CollaborativeCollection):
            return forms.CollaborativeCollectionForm
        return forms.CollectionForm

    def get_initial(self):
        """Add initial form values."""
        initial = super().get_initial()
        collection = getattr(self.object, "collection_ptr", self.object)
        users_groups = CollectionsGroup.objects.filter(
            owner=self.request.user
        ).values_list("pk", flat=True)
        initial.update(
            self.get_form_class().get_collection_form_initial(collection, users_groups)
        )
        return initial

    def get_form_kwargs(self):
        """Check if is a Collaborative  Collection and pass the instance."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_object(self, queryset=None):
        """Return an instance of the requested object."""
        collection_instance = super().get_object(queryset)
        return getattr(
            collection_instance, "collaborativecollection", collection_instance
        )

    def post(self, request, *args, **kwargs):
        """Handle deletion of Collections."""
        if "delete" in self.request.POST:
            collection = self.get_object()
            Collection.objects.filter(pk=collection.pk).delete()
            messages.success(request, _("Tu colección se ha eliminado."))
            return HttpResponseRedirect(reverse("my_collections"))
        return super().post(request, *args, **kwargs)


class CollectionsGroupEditView(
    CachedObjectMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Edit an existent Collections Group."""

    form_class = forms.CollectionsGroupForm
    raise_exception = True
    template_name = "harvester/collectionsgroup_form.html"
    success_message = _("Grupo de colecciones modificado correctamente.")
    queryset = CollectionsGroup.objects.all()

    def test_func(self):
        """Only allow access to owner of the collection."""
        return self.request.user == self.get_object().owner

    def post(self, request, *args, **kwargs):
        """Handle deletion of Collections."""
        if "delete" in self.request.POST:
            collections_group = self.get_object()
            if collections_group.title.lower() == "favoritos":
                messages.error(
                    request,
                    _("No puedes eliminar tu grupo de colecciones 'favoritos'."),
                )
            else:
                self.get_object().delete()
                messages.success(request, _("Tu grupo de colecciones se ha eliminado."))
            return HttpResponseRedirect(reverse("collectionsgroups"))
        return super().post(request, *args, **kwargs)


class CollectionCollaboratorsFormView(
    UserPassesTestMixin, BaseUserSearchSelectFormViewMixin
):
    """Update Collaborators for Collections."""

    raise_exception = True
    template_name = "harvester/collection_collaborators_form.html"
    form_class = forms.CollectionsCollaboratorsForm
    success_message = _("Invitaciones enviadas.")
    model = CollaborativeCollection

    def test_func(self):
        """Only the Collection owner can access."""
        return self.request.user == self.get_object().owner

    def render_users_autocomplete(self):
        """Return a list of users valid for Collaborate."""
        search_text = self.request.GET.get("search_text")
        users_queryset = self.get_form_class().get_valid_users_queryset(self.object)
        User = get_user_model()
        results_queryset = users_queryset.search(search_text)[:20]
        response = User.format_search_users_result_queryset(
            results_queryset, search_text
        )
        return JsonResponse(response)


class CollectionListView(
    CancellShareMessageMixin, CollectionsGroupsFormsetMixin, OrderingMixin, ListView
):
    """List Collections."""

    model = Collection
    queryset = (
        model.objects.visible()
        .exclude_subclasses()
        .filter(public=True)
        .exclude(resources_count_cached=0)
        .annotate_groups()
    )
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-updated_at"]),
        "-recent": (_("Menos reciente"), ["updated_at"]),
    }
    default_ordering = ordering = ["-resources_count_cached", "-updated_at"]

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE

    def get_promoted(self):
        """Return promoted elements with home_internal."""
        return self.queryset.filter(home_internal=True)

    def get_context_data(self, **kwargs):  # pylint: disable=arguments-differ
        """Get the context for this view."""
        context = super().get_context_data(**kwargs)
        context["promoted"] = self.get_promoted()
        return context

    def get(self, request, *args, **kwargs):
        self.collections_formset_object_list = self.get_collections_formset_initial()
        return super().get(request, *args, **kwargs)


class CollectionsGroupListView(LoginRequiredMixin, OrderingMixin, ListView):
    """List Collections."""

    model = CollectionsGroup

    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-updated_at"]),
        "-recent": (_("Menos reciente"), ["updated_at"]),
    }

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE

    def get_queryset(self):
        """List only user's collections groups."""
        queryset = super().get_queryset()
        return (
            queryset.filter(owner=self.request.user)
            .exclude(title="favoritos")
            .distinct()
        )


class MyCollectionListView(LoginRequiredMixin, CollectionListView):
    """List logged user's collections."""

    model = Collection
    queryset = model.objects.visible().annotate_groups().exclude_subclasses()
    template_name = "harvester/mycollection_list.html"
    default_ordering = ordering = ("-resources_count_cached", "-updated_at")

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE

    def get_queryset(self):
        """Filter collections by logged user."""
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user).distinct()


class CollaborativeCollectionListView(
    CancellShareMessageMixin, CollectionsGroupsFormsetMixin, OrderingMixin, ListView
):
    """List Collaborative Collections."""

    model = CollaborativeCollection
    queryset = (
        model.objects.visible()
        .annotate_groups()
        .filter(public=True)
        .exclude(resources_count_cached=0)
    )
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-updated_at"]),
        "-recent": (_("Menos reciente"), ["updated_at"]),
    }
    default_ordering = ordering = ["-resources_count_cached", "-updated_at"]

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE

    def get(self, request, *args, **kwargs):
        self.collections_formset_object_list = self.get_collections_formset_initial()
        return super().get(request, *args, **kwargs)


class MyCollaborativeCollectionListView(
    LoginRequiredMixin, CollaborativeCollectionListView
):
    """List logged user's Collaborative Collections."""

    model = CollaborativeCollection
    queryset = model.objects.visible().annotate_groups()
    template_name = "harvester/mycollaborativecollection_list.html"
    default_ordering = ordering = ["-resources_count_cached", "-updated_at"]

    def get_queryset(self):
        """Filter collections by logged user."""
        queryset = super().get_queryset()
        return queryset.filter(
            Q(owner=self.request.user)
            | Q(collaborators__in=[self.request.user]) & Q(collaborator__status=1)
        ).distinct()


class SetDetailView(
    CancellShareMessageMixin,
    SearchFormWithSetFilterMixin,
    UserPassesTestMixin,
    FilteringMixin,
    OrderingMixin,
    PaginatorMixin,
    SuccessMessageMixin,
    ProcessFormView,
    ModelFormMixin,
    DetailView,
):
    """Show details of a Set."""

    model = Set
    queryset = model.objects.visible().annotate_groups()

    paginated_objects_name = "resources"
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title__0"]),
        "za": (_("De la Z a la A"), ["-title__0"]),
        "recent": (_("Más reciente"), ["-calculated_date"]),
        "-recent": (_("Menos reciente"), ["calculated_date"]),
    }
    filters_form_class = forms.ContentResourceFilters
    form_class = forms.SetForm

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        super().setup(request, *args, **kwargs)
        self.success_url = self.request.get_full_path()

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        set = self.get_object()
        users_groups = CollectionsGroup.objects.filter(
            owner=self.request.user
        ).values_list("pk", flat=True)
        return self.get_form_class().get_collections_groups_form_initial(
            set, users_groups
        )

    def get_form(self, form_class=None):
        """Return instances of the form for authenticated users."""
        if self.request.user.is_anonymous:
            return None
        return super().get_form(form_class)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        """Only allow POST to owner of the collection."""
        if self.request.method.lower() == "post":
            if self.request.user.is_anonymous:
                return False
        return True

    def get(self, request, *args, **kwargs):
        """
        Handle GET request.

        Set a paginatable resources queryset.
        """
        self.object = self.get_object()
        self.paginatable_queryset = self.order_queryset(
            self.filter_queryset(
                self.object.contentresource_set.visible().order_by("id")
            )
        ).distinct()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request.
        """
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        if cleaned_data["collections_groups"]:
            groups_names = ", ".join(
                cleaned_data["collections_groups"].values_list("title", flat=True)
            )
            return _(f"Has agregado esta colección a los grupos {groups_names}")
        return _("La colección ya no esta asignada a ningún grupo.")


class SetListView(
    CollectionsGroupsFormsetMixin, FilteringMixin, OrderingMixin, ListView
):
    """List Collaborative Collections."""

    model = Set
    queryset = model.objects.visible().prefetch_related("data_source").annotate_groups()
    ordering_options = {
        "az": (_("De la a A a la Z"), ["name"]),
        "za": (_("De la Z a la A"), ["-name"]),
        "recent": (_("Más reciente"), ["-updated_at"]),
        "-recent": (_("Menos reciente"), ["updated_at"]),
    }
    filters_form_class = forms.SetFilters

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE

    def get_queryset(self):
        """Return the filtered queryset."""
        return self.filter_queryset(super().get_queryset()).prefetch_related(
            "data_source"
        )

    def get_promoted(self):
        """Return promoted elements with home_internal."""
        return self.queryset.prefetch_related("data_source").filter(home_internal=True)

    def get_context_data(self, **kwargs):  # pylint: disable=arguments-differ
        """Get the context for this view."""
        context = super().get_context_data(**kwargs)
        context["promoted"] = self.get_promoted()
        return context

    def get(self, request, *args, **kwargs):
        self.collections_formset_object_list = self.get_collections_formset_initial()
        return super().get(request, *args, **kwargs)


class DynamicUrlRegexSampleView(PermissionRequiredMixin, DetailView):
    """Load samples for Image Dynamic URL."""

    model = DataSource
    permission_required = "change_datasource"

    def get(self, request, *args, **kwargs):
        """Pass params to Content Resource Processor to get Dynamic Url."""
        data_source = self.get_object()
        field = request.GET.get("field", None)
        capture = request.GET.get("capture_expression", None)
        replace = request.GET.get("replace_expression", None)
        resources = ContentResource.objects.filter(data_source=data_source)[:5]
        urls = []
        for resource in resources:
            values = getattr(resource, field)
            try:
                (
                    matched_value,
                    replaced,
                ) = ContentResourceProcessor.resolve_dynamic_image(
                    values=values, capture=capture, replace_string=replace
                )
            except (TypeError, IndexError):
                urls.append(
                    [
                        _(
                            "El campo %(field)s no contiene información que coincida"
                            " con la expresión de captura"
                        )
                        % {"field": field},
                        "--",
                    ]
                )
            else:
                urls.append(
                    (
                        matched_value if matched_value is not None else values,
                        (
                            replaced
                            if replaced is not None
                            else _("Ningún valor coincide con la expresión.")
                        ),
                    )
                )
        return JsonResponse(urls, safe=False)


class DynamicIdentifierSampleView(PermissionRequiredMixin, DetailView):
    """Load samples for Dynamic Identifier."""

    model = DataSource
    permission_required = "change_datasource"

    def get(self, request, *args, **kwargs):
        """Pass params to Content Resource to calculate the Dynamic Identifier."""
        data_source = self.get_object()
        fields = request.GET.getlist("fields[]")
        expressions = request.GET.getlist("expressions[]")
        new_config = [
            DynamicIdentifierConfig(
                data_source=data_source,
                field=field,
                capture_expression=expressions[index],
            )
            for index, field in enumerate(fields)
            if field != ""
        ]
        resources = ContentResource.objects.filter(data_source=data_source)[:5]
        urls = []

        for resource in resources:
            values = [
                getattr(resource, config_pair.field) for config_pair in new_config
            ]
            dynamic_identifier = resource.calculate_dynamic_identifier(
                configs=new_config, resource_data=resource
            )
            urls.append(
                (
                    (
                        values
                        if values
                        else _("El campo seleccionado no contiene valores.")
                    ),
                    (
                        dynamic_identifier
                        if dynamic_identifier
                        else _("Ningún valor coincide con la expresión.")
                    ),
                )
            )
        return JsonResponse(urls, safe=False)


class ServeHumansView(TemplateView):
    """Serve the humans.txt"""

    content_type = "text/plain"

    def get_template_names(self):
        """Set the template name."""
        return "humans.txt"


class ServeRobotsView(TemplateView):
    content_type = "text/plain"

    def get_template_names(self):
        if (
            getattr(settings, ROBOTS_ALLOW_HOST_SETTING, None)
            == self.request.get_host()
        ):
            return ROBOTS_ALLOW_TEMPLATE
        return ROBOTS_DISALLOW_TEMPLATE


class ReviewEditView(
    CancellShareMessageMixin,
    GoBackUrlMixin,
    CachedObjectMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Edit an existent Collection."""

    raise_exception = True
    template_name = "harvester/review_form.html"
    success_message = _("Reseña modificada correctamente.")
    model = Review
    review_permissions = ["harvester.add_review"]
    form_class = ReviewForm

    def test_func(self):
        """Only allow access to author of the review."""
        return (
            self.request.user.has_perms(self.review_permissions)
            and self.request.user == self.get_object().author
        )

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        form.save()
        if "next" in self.request.GET:
            success_url = self.request.GET["next"]
        else:
            success_url = reverse("my_reviews")
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return HttpResponseRedirect(success_url)


class ReviewAddView(
    CancellShareMessageMixin,
    GoBackUrlMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    SuccessMessageMixin,
    SingleObjectTemplateResponseMixin,
    ModelFormMixin,
    ProcessFormView,
):
    """Edit an existent Collection."""

    raise_exception = True
    template_name = "harvester/review_form.html"
    success_message = _("Reseña agregada correctamente.")
    queryset = Review.objects.select_related("resource").all()
    review_permissions = ["harvester.add_review"]
    form_class = ReviewForm
    object = None

    def test_func(self):
        """Only allow access to author of the review."""
        return self.request.user.has_perms(self.review_permissions)

    def get_object(self, queryset=None):
        if self.object is None and "resource" in self.request.GET:
            resource = get_object_or_404(
                ContentResource, pk=self.request.GET["resource"]
            )
            object = Review(author=self.request.user, resource=resource)
            return object
        return self.object

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            return super().get(request, *args, **kwargs)
        raise Http404()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            return super().post(request, *args, **kwargs)
        raise Http404()


class MyReviewListView(
    CancellShareMessageMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    OrderingMixin,
    reviewFormActionsMixin,
    ListView,
):
    """List Reviews."""

    model = Review
    queryset = model.objects.select_related("resource").all()
    review_permissions = ["harvester.add_review"]
    template_name = "harvester/myreview_list.html"
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-updated_at"]),
        "-recent": (_("Menos reciente"), ["updated_at"]),
    }
    success_message = ""

    def test_func(self):
        """Only allow access to users with permissions."""
        return self.request.user.has_perms(self.review_permissions)

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE

    def get_queryset(self):
        """Filter reviews by logged user."""
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user).distinct()

    def get_success_url(self):
        return reverse("my_reviews")
