"""Define Views for custom user app."""
from urllib import parse

from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Prefetch, Q
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, UpdateView

from custom_user.forms import ProfileForm
from custom_user.models import Profile
from harvester.models import (CollaborativeCollection, Collection, Set,
                              SharedResource)
from resources.views import OrderingMixin, PaginatorMixin

from .forms import (InvitationsForm, MegaRedAuthenticationForm,
                    NotificationForm, RequestsForm)
from .models import Country

User = get_user_model()  # pylint: disable=invalid-name


class MegaRedLoginView(LoginView):
    """Define an authentication view that uses MegaRed form."""

    authentication_form = MegaRedAuthenticationForm
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.

        If `exclusive` comes as a GET parameter, display a message about
        content being exclusive.
        """
        if "exclusive" in request.GET:
            messages.warning(
                self.request,
                _(
                    "Para acceder a este contenido necesitas iniciar sesión con una cuenta "
                    "de BibloRed."
                ),
            )
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        """Populate `initial` with data from GET params."""
        initial = super().get_initial()

        initial["country"] = Country.objects.filter(name__iexact="colombia").first()

        if "username" in self.request.GET:
            initial["username"] = str(self.request.GET["username"])

        if "country" in self.request.GET:
            try:
                dian_code = int(self.request.GET["country"])
            except ValueError:
                pass
            else:
                initial["country"] = Country.objects.filter(dian_code=dian_code).first()

        return initial

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        response = super().form_valid(form)
        if form.cleaned_data.get("remember"):
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return response

    def get_success_url_allowed_hosts(self):
        """Set all Institutional Collection Urls as Safe for Redirect."""
        success_url_allowed_hosts = [
            parse.urlparse(a_set.data_source_url).netloc
            for a_set in Set.objects.filter(data_source_url__isnull=False)
            .distinct()
            .only("data_source_url")
        ]
        return {self.request.get_host(), *success_url_allowed_hosts}


class MegaRedProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Define View to edit a User's Profile."""

    model = Profile
    form_class = ProfileForm

    def setup(self, request, *args, **kwargs):
        """Add current user as default argument if one is not present."""
        if not kwargs.get("pk") and request.user.is_authenticated:
            kwargs["pk"] = request.user.pk

        if REDIRECT_FIELD_NAME in request.GET:
            self.success_url = request.GET[REDIRECT_FIELD_NAME]

        super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get or create a Profile with given pk."""
        try:
            return super().get_object(queryset)
        except Http404:
            pass

        user = super().get_object(User.objects)
        return Profile.objects.create(user=user)

    def get_success_message(self, cleaned_data):
        """Return a success_message based on performed action."""
        return _("Tu perfil se ha modificado con éxito")


class MegaRedAnotherUserProfileView(OrderingMixin, PaginatorMixin, DetailView):
    """Define a profile view for users."""

    model = Profile
    template_name = "custom_user/another_user_profile_detail.html"
    paginated_objects_name = "individualcollections"
    allowed_collections = {
        "individualcollections": Collection,
        "collaborativecollections": CollaborativeCollection,
    }
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-updated_at"]),
        "-recent": (_("Menos reciente"), ["updated_at"]),
    }
    object = None

    def dispatch(self, request, *args, **kwargs):
        """Return queryset that preloads related Collections."""
        requested_collections = request.GET.get("collections")
        if requested_collections in self.allowed_collections.keys():
            self.paginated_objects_name = requested_collections

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get or create a Profile with given pk."""
        if self.object:
            return self.object

        try:
            return super().get_object(queryset)
        except Http404:
            pass

        user = super().get_object(User.objects)
        return Profile.objects.create(user=user)

    def get(self, request, *args, **kwargs):
        """
        Handle GET request.

        Includes the Collection queryset to be paginated.
        """
        if request.user.is_authenticated and kwargs["pk"] == request.user.pk:
            return HttpResponseRedirect(reverse("profile"))
        self.object = self.get_object()
        self.paginatable_queryset = self.order_queryset(self.get_collections())
        return super().get(request, *args, **kwargs)

    def get_collections(self):
        """Return a queryset of requested collections type."""
        collection_class = self.allowed_collections[self.paginated_objects_name]
        queryset = collection_class.objects.visible()
        or_filters = Q(owner=self.object.user)

        if collection_class is CollaborativeCollection:
            or_filters = or_filters | (
                Q(collaborators__in=[self.object.user]) & Q(collaborator__status=1)
            )

        if self.request.user != self.object.user:
            queryset = queryset.filter(public=True)

        if collection_class is Collection:
            queryset = queryset.exclude_subclasses()

        return queryset.filter(or_filters).distinct().all()

    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset, if needed."""
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get("page") or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == "last":
                page_number = paginator.num_pages
            else:
                raise Http404(
                    _("Page is not 'last', nor can it be converted to an int.")
                )
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as exception:
            raise Http404(
                _("Invalid page (%(page_number)s): %(message)s")
                % {"page_number": page_number, "message": str(exception)}
            )


class MegaRedProfileBaseView(PaginatorMixin, LoginRequiredMixin, DetailView):
    """Define a profile view for users."""

    paginate_by = config.PAGE_SIZE
    model = Profile
    object = None

    def setup(self, request, *args, **kwargs):
        """Add current user as default argument if one is not present."""
        if not kwargs.get("pk") and request.user.is_authenticated:
            kwargs["pk"] = request.user.pk

        super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get or create a Profile with given pk."""
        if self.object:
            return self.object

        try:
            return super().get_object(queryset)
        except Http404:
            pass

        user = super().get_object(User.objects)
        return Profile.objects.create(user=user)

    def get(self, request, *args, **kwargs):
        """
        Handle GET request.

        Includes the Collection queryset to be paginated.
        """
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class MegaRedProfileWithInvitationsView(
    SuccessMessageMixin, FormView, MegaRedProfileBaseView
):
    """Define a profile view for users with invitations list."""

    template_name = "custom_user/profile_detail_invitations.html"
    model = Profile
    object = None
    form_class = InvitationsForm
    paginated_objects_name = "invitations"

    def get_form_kwargs(self):
        """Set Logged in user as parameter to form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["notifications"] = self.request.user.invitations
        return form_kwargs

    def form_valid(self, form):
        """Call form save."""
        form.save()
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        """Return a success_message based on performed action."""
        collaborator = cleaned_data.get("accept", None) or cleaned_data.get(
            "reject", None
        )
        if cleaned_data["accept"]:
            return _("Ahora colaboras en la colección %(collection_title)s") % {
                "collection_title": collaborator.collaborativecollection.title
            }

        if cleaned_data["reject"]:
            return _("Se ha rechazado la solicitud para colaborar")

        return super().get_success_message(cleaned_data)

    def get_paginatable_queryset(self):
        """Get the paginatable queryset."""
        return self.request.user.invitations.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("profile-invitations")


class MegaRedProfileWithRequestsView(MegaRedProfileWithInvitationsView):
    """Define a profile view for users with requests list."""

    template_name = "custom_user/profile_detail_requests.html"
    paginated_objects_name = "requests"
    form_class = RequestsForm

    def get_form_kwargs(self):
        """Set Logged in user as parameter to form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["notifications"] = self.request.user.requests
        return form_kwargs

    def get_success_message(self, cleaned_data):
        """Return a success_message based on performed action."""
        collaborator = cleaned_data.get("accept", None) or cleaned_data.get(
            "reject", None
        )
        if cleaned_data["accept"]:
            return _("%(collaborator_name)s ahora colabora en tu colección") % {
                "collaborator_name": collaborator.user.full_name
            }

        if cleaned_data["reject"]:
            return _("Se ha rechazado la solicitud para colaborar")

        return super().get_success_message(cleaned_data)

    def get_paginatable_queryset(self):
        """Get paginatable the queryset."""
        return self.request.user.requests.filter(
            collaborativecollection__owner=self.request.user
        )

    def get_success_url(self):
        return reverse("profile-requests")


class MegaRedProfileWithSharedResourcesView(MegaRedProfileBaseView):
    """Define a profile view for users."""

    template_name = "custom_user/profile_detail_shared_resources.html"
    model = Profile
    object = None
    paginated_objects_name = "shared_resources_notifications"

    def get_paginatable_queryset(self):
        """Get paginatable the queryset."""
        return (
            self.request.user.sharedresourceuser_set.prefetch_related(
                Prefetch(
                    "shared_resource",
                    queryset=SharedResource.objects.select_related("owner")
                    .select_related("resource")
                    .all(),
                )
            )
            .exclude(status=2)
            .order_by("status", "-created_at")
        )

    def get_success_url(self):
        return reverse("profile-share-resources")


class NotificationsView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """View to accept/decline Notifications (requests, invitations)."""

    paginate_by = config.PAGE_SIZE
    template_name = "custom_user/notification_list_page.html"
    form_class = NotificationForm

    def get_form_kwargs(self):
        """Set Logged in user as parameter to form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_success_url(self):
        """Return to the notifications url."""
        if "next" in self.request.GET:
            return f'{self.request.GET["next"]}'
        return reverse("notifications")

    def form_valid(self, form):
        """Call form save."""
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        """Call to the form validation and save or fail."""
        form = self.get_form()
        if form.is_valid():
            return super().post(request, *args, **kwargs)

        return self.form_invalid(form)

    def get_success_message(self, cleaned_data):
        """Return a success_message based on performed action."""
        collaborator = cleaned_data.get("accept", None) or cleaned_data.get(
            "reject", None
        )
        if cleaned_data["accept"]:
            if collaborator.collaborativecollection.owner == self.request.user:
                return _("%(collaborator_name)s ahora colabora en tu colección") % {
                    "collaborator_name": collaborator.user.full_name
                }

            if collaborator.user == self.request.user:
                return _("Ahora colaboras en la colección %(collection_title)s") % {
                    "collection_title": collaborator.collaborativecollection.title
                }

        if cleaned_data["reject"]:
            return _("Se ha rechazado la solicitud para colaborar")

        return super().get_success_message(cleaned_data)

    def get_context_data(self, **kwargs):
        """Return the context, that include invitations and requests."""
        context = super().get_context_data(**kwargs)
        collection_id = self.request.GET.get("collection")
        invitations_filter_by = Q(user=self.request.user)
        requests_filter_by = Q(collaborativecollection__owner=self.request.user)
        if collection_id:
            collection_filter = Q(collaborativecollection__pk=collection_id)
            invitations_filter_by &= collection_filter
            requests_filter_by &= collection_filter

        context["invitations"] = self.request.user.requests_and_invitations.filter(
            invitations_filter_by
        )
        context["requests"] = self.request.user.requests_and_invitations.filter(
            requests_filter_by
        )
        return context
