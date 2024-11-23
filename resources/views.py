"""Define views for the Resources app."""

import os
from datetime import timedelta
from itertools import chain
from operator import attrgetter

from advanced_filters.views import GetFieldChoices
from constance import config
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Count
from django.http import (
    Http404,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from expositions.models import Exposition
from harvester.forms.forms import (
    BaseCollectionAddToGroupsFormSet,
    CollectionAddToGroupsForm,
)
from django.db.models import F
from harvester.models import (
    Collection,
    CollectionsGroup,
    ContentResource,
    ContentResourceEquivalence,
    DataSource,
    Equivalence,
    PromotedContentResource,
    Set,
)

User = get_user_model()  # pylint: disable=invalid-name


class CachedObjectMixin:
    """Provide a `get_object` method that uses an existing object if possible."""

    object = None

    def get_object(self, queryset=None):
        """
        Return the object instance for the current resource.

        This tries to returns an existing object to avoid extra DB queries.
        """
        if self.object:
            return self.object

        return super().get_object(queryset)


class OrderingMixin:
    """
    Provide multiple options for ordering.

    `ordering_options` should be a dictionary where keys are the value
    of the parameter on the request, and the values are tuples with the
    label to show the user and the fields to pass to the queryset `order_by` method.

    `default_ordering` is the default order when no param is received.

    Example:
    ```
    ordering_options = {
        "az": (_("Alphabetically"), ["-name"]),
    }
    default_ordering = "az"
    ```

    """

    ordering_options = None
    default_ordering = None

    def order_queryset(self, queryset):
        """Apply ordering and return the ordered queryset."""
        ordering = self.get_ordering()
        if ordering:
            asc_ordering_field_names = [
                field_name for field_name in ordering if not field_name.startswith("-")
            ]
            desc_ordering_field_names = [
                str(field_name).replace("-", "")
                for field_name in ordering
                if field_name.startswith("-")
            ]

            for desc_field in desc_ordering_field_names:
                queryset = queryset.order_by(F(desc_field).desc(nulls_last=True))

            for asc_field in asc_ordering_field_names:
                queryset = queryset.order_by(F(asc_field).asc(nulls_last=True))
        return queryset

    def order_queryset_list(self, queryset_list):
        """Apply ordering and return the ordered object list."""
        ordering = self.get_ordering()
        print(ordering)
        if ordering:
            order_by = ordering[0]
            if order_by.startswith("-"):
                reverse = True
                order_by = order_by.replace("-", "")
            else:
                reverse = False
            if order_by == "title":
                object_list = sorted(
                    chain(*queryset_list),
                    key=lambda collection: (
                        collection.title
                        if hasattr(collection, "title")
                        else collection.name
                    ),
                    reverse=reverse,
                )
            else:
                object_list = sorted(
                    chain(*queryset_list),
                    key=attrgetter(order_by),
                    reverse=reverse,
                )
        else:
            object_list = [object for objects in queryset_list for object in objects]
        return object_list

    def order_mixed_queryset(self, mixed_queryset):
        """Apply ordering and return the ordered object list."""
        # TODO esto es innecesario pero hay que refactorizar el annotated
        ordering = self.get_ordering()
        print(ordering)
        if ordering:
            order_by = ordering[0]
            if order_by.startswith("-"):
                reverse = True
                order_by = order_by.replace("-", "")
            else:
                reverse = False
            if order_by == "title":
                object_list = sorted(
                    mixed_queryset,
                    key=lambda collection: (
                        collection.content_object.title
                        if hasattr(collection.content_object, "title")
                        else collection.content_object.name
                    ),
                    reverse=reverse,
                )
            else:
                object_list = sorted(
                    mixed_queryset,
                    key=attrgetter(order_by),
                    reverse=reverse,
                )
        else:
            object_list = list(mixed_queryset.iterator())
        return object_list

    def get_applied_ordering(self):
        """Return the order_by option to use."""
        order_by = self.request.GET.get("order_by")
        if order_by in self.ordering_options:
            return order_by
        return None

    def get_ordering(self):
        """Return the field or fields to use for ordering the queryset."""
        applied_ordering = self.get_applied_ordering()
        if applied_ordering:
            return self.ordering_options[applied_ordering][1]

        return self.default_ordering

    def get_context_data(self, **kwargs):
        """Add ordering variables to context."""
        context = super().get_context_data(**kwargs)
        context["ordering_options"] = {
            key: options[0] for key, options in self.ordering_options.items()
        }
        context["applied_ordering"] = self.get_applied_ordering()
        return context


class FilteringMixin:
    """
    Provide form processing for queryset filters.

    a `form_filter_class` must be provided. The form will be instantiated
    with an instance of the queryset that the filters should be applied to.
    """

    filters_form_class = None
    filters_form = None

    def filter_queryset(self, queryset):
        """Apply filters and return the filtered queryset."""
        if not queryset.exists():
            return queryset

        self.filters_form = self.filters_form_class(  # pylint: disable=not-callable
            queryset=queryset, data=self.request.GET
        )
        return self.filters_form.filtered_queryset()

    def get_context_data(self, **kwargs):
        """Add ordering variables to context."""
        context = super().get_context_data(**kwargs)
        context["filters_form"] = self.filters_form
        return context


class PaginatorMixin:
    """Mixin for easy pagination in Class views."""

    paginated_objects_name = None
    paginatable_queryset = None

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        if not hasattr(self, "paginate_by"):
            self.paginate_by = config.PAGE_SIZE

    def get_paginatable_queryset(self):
        """Get paginatable the queryset."""
        return self.paginatable_queryset

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

    def get_context_data(self, **kwargs):
        """Add pagination variables to context."""
        context = super().get_context_data(**kwargs)

        if self.paginatable_queryset is None:
            self.paginatable_queryset = self.get_paginatable_queryset()

        if (
            self.paginated_objects_name is not None
            and self.paginatable_queryset is not None
        ):
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                self.paginatable_queryset, self.paginate_by
            )
            context.update(
                {
                    "paginator": paginator,
                    "page_obj": page,
                    "is_paginated": is_paginated,
                    self.paginated_objects_name: queryset,
                }
            )
        return context


class MultiFormSuccessMessageMixin:
    """Success message mixin that handle MultiFormMixin forms_valid."""

    success_message = ""

    def forms_valid(self, forms, form_name):
        response = super().forms_valid(forms, form_name)
        success_message = self.get_success_message(
            forms[form_name].cleaned_data, form_name
        )
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data, form_name=None):
        return self.success_message % cleaned_data


class MultiFormMixin(ContextMixin):
    """
    Handle Multiple Forms in a view.
    reference:
      codementor.io/@lakshminp/handling-multiple-forms-on-the-same-page-in-django-fv89t2s3j
    """

    form_classes = {}
    prefixes = {}
    success_urls = {}

    initial = {}
    prefix = None
    success_url = None

    json_response = False

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes):
        return dict(
            [
                (key, self._create_form(key, class_name))
                for key, class_name in form_classes.items()
            ]
        )

    def get_form_kwargs(self, form_name):
        kwargs = {}
        kwargs.update({"initial": self.get_initial(form_name)})
        kwargs.update({"prefix": self.get_prefix(form_name)})
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        get_form_kwargs_method = "get_%s_form_extra_kwargs" % form_name
        if hasattr(self, get_form_kwargs_method):
            kwargs.update(getattr(self, get_form_kwargs_method)())
        return kwargs

    def forms_valid(self, forms, form_name):
        form_valid_method = "%s_form_valid" % form_name
        if hasattr(self, form_valid_method):
            return getattr(self, form_valid_method)(forms[form_name], form_name)
        else:
            return HttpResponseRedirect(self.get_success_url(form_name))

    def forms_invalid(self, forms, form_name):
        form_invalid_method = "%s_form_invalid" % form_name
        if hasattr(self, form_invalid_method):
            return getattr(self, form_invalid_method)(forms)
        else:
            return self.render_to_response(self.get_context_data(forms=forms))

    def get_initial(self, form_name):
        initial = {"form_name": form_name}
        initial_method = "get_%s_extra_initial" % form_name
        if hasattr(self, initial_method):
            initial.update(getattr(self, initial_method)())
        return initial

    def get_prefix(self, form_name):
        return self.prefixes.get(form_name, self.prefix)

    def get_success_url(self, form_name=None):
        if form_name in self.success_urls:
            return self.success_urls.get(form_name)
        elif self.success_url:
            return self.success_url
        else:
            return self.request.get_full_path()

    def _create_form(self, form_name, form_class):
        form_kwargs = self.get_form_kwargs(form_name)
        form = form_class(**form_kwargs)
        return form

    def get_context_data(self, **kwargs):
        """Insert the forms into the context dict."""
        if "forms" not in kwargs:
            kwargs["forms"] = self.get_forms(self.get_form_classes())
        return super().get_context_data(**kwargs)


class ProcessMultipleFormsMixin:
    """
    Process one of multiple Forms in a view.
    reference:
      codementor.io/@lakshminp/handling-multiple-forms-on-the-same-page-in-django-fv89t2s3j
    """

    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        form_name = request.POST.get("form_name")
        return self._process_individual_form(form_name, form_classes)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes)
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms, form_name)


class BaseMultipleFormsMixin(MultiFormMixin, ProcessMultipleFormsMixin):
    """
    A base view for displaying several forms.
    reference:
      codementor.io/@lakshminp/handling-multiple-forms-on-the-same-page-in-django-fv89t2s3j
    """


class MultiFormsMixin(TemplateResponseMixin, BaseMultipleFormsMixin):
    """
    A view for displaying several forms, and rendering a template response.
    reference:
      codementor.io/@lakshminp/handling-multiple-forms-on-the-same-page-in-django-fv89t2s3j
    """


class CollectionInMultiformMixin:
    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        super().setup(request, *args, **kwargs)
        self.success_urls["collection"] = self.request.get_full_path()

    def get_form_classes(self):
        """Add collection form class."""
        form_classes = super().get_form_classes()
        if "collection" not in form_classes:
            form_classes["collection"] = CollectionAddToGroupsForm
        return form_classes

    def get_collection_extra_initial(self):
        """Pass the object instance to form."""
        users_groups = CollectionsGroup.objects.filter(
            owner=self.request.user
        ).values_list("pk", flat=True)
        return self.get_form_classes()[
            "collection"
        ].get_collections_groups_form_initial(self.get_object(), users_groups)

    def get_collection_form_extra_kwargs(self):
        """Pass the object instance to form."""
        return {"instance": self.get_object(), "user": self.request.user}

    def get_success_url(self, form_name=None):
        if form_name == "collection":
            return self.request.get_full_path()
        return super().get_success_url(form_name)

    def collection_form_valid(self, form, form_name):
        """Save collection form."""
        form.save()

    def get_success_message(self, cleaned_data, form_name=None):
        """Show a message when post is successful."""
        if form_name == "collection":
            if cleaned_data["collections_groups"]:
                groups_names = ", ".join(
                    cleaned_data["collections_groups"].values_list("title", flat=True)
                )
                return _(f"Has agregado esta colección a los grupos {groups_names}")
            return _("La colección ya no esta asignada a ningún grupo.")
        return super().get_success_message(cleaned_data, form_name)


class CollectionsGroupsFormsetMixin:
    collections_formset_form_class = CollectionAddToGroupsForm
    collections_formset_prefix = "collection"
    collections_formset_object_list = []
    users_groups = []

    def get_user_groups(self):
        if not self.users_groups and self.request.user.is_authenticated:
            self.users_groups = CollectionsGroup.objects.filter(
                owner=self.request.user
            ).values_list("pk", flat=True)
        return self.users_groups

    def get_collections_formset_initial(self):
        """Return the data parameter for instantiating the collections formset."""
        # TODO esto es innecesario pero hay que refactorizar el annotated
        initial = []
        user_groups = self.get_user_groups()
        object_list = self.collections_formset_object_list
        if hasattr(self, "paginator_class"):
            paginator = self.paginator_class(self.get_queryset(), self.paginate_by)
            object_list = paginator.page(
                self.request.GET.get(self.page_kwarg, 1)
            ).object_list

        for object_instance in object_list:
            form_initial = (
                self.collections_formset_form_class.get_collections_groups_form_initial(
                    object_instance, user_groups
                )
            )
            form_initial.update({"instance": object_instance})
            initial.append(form_initial)

        return initial

    def get_collections_form_kwargs(self):
        """Get collections formset kwargs."""
        kwargs = {"user": self.request.user}
        return kwargs

    def get_collections_formset_kwargs(self):
        """Return the keyword arguments for instantiating the collections formset."""
        return {
            "prefix": self.collections_formset_prefix,
            "initial": self.get_collections_formset_initial(),
            "form_kwargs": self.get_collections_form_kwargs(),
        }

    def get_collections_formset(self):
        """Get collections formset."""
        formset_class = forms.formset_factory(
            self.collections_formset_form_class,
            formset=BaseCollectionAddToGroupsFormSet,
            extra=0,
        )
        return formset_class(**self.get_collections_formset_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collections_formset"] = self.get_collections_formset()
        return context


class HomeView(CollectionsGroupsFormsetMixin, TemplateView):
    """Define and render the Home view."""

    template_name = "biblored/pages/home.html"
    __collections = None
    __most_read = None
    __based_on_reads = None

    @property
    def collections(self):
        if self.__collections is None:
            queryset = (
                Collection.objects.annotate_groups()
                .visible()
                .prefetch_related("collaborativecollection")
                .exclude(
                    # Exclude Subchildren
                    Collection.objects.get_subclasses_excludes(),
                    # Only if are not CollaborativeCollection
                    collaborativecollection__isnull=True,
                )
                .filter(public=True, home_site=True)
                .all()[:4]
            )
            collections = []
            for collection in queryset:
                collections.append(
                    getattr(collection, "collaborativecollection", collection)
                )
            self.__collections = collections
        return self.__collections

    @property
    def get_based_on_reads(self):
        """Return a list of the Based on Your Reads ContentResources."""
        if self.__based_on_reads is None:
            self.__based_on_reads = (
                ContentResource.objects.filter(hitcount__hit__user=self.request.user)
                .annotate(hits=Count("hitcount__hit"))
                .visible()
                .order_by("-hits", "data_source__relevance")[:2]
            )
        return self.__based_on_reads

    @property
    def get_most_read(self):
        """
        Return queryset for most popular ContentResource by collection count.

        Only include resources that have been added to a collection in the last 7 days.
        """
        seven_days_ago = timezone.now() + timedelta(days=-7)
        if self.__most_read is None:
            self.__most_read = (
                ContentResource.objects.visible()
                .filter(
                    data_source__online_resources=True,
                    collectionandresource__isnull=False,
                )
                .annotate(Count("collectionandresource"))
                .filter(collectionandresource__created_at__gt=seven_days_ago)
                .order_by("-collectionandresource__count")[:6]
            )

        return self.__most_read

    @staticmethod
    def get_curated_collections():
        """Return a list of Sets selected by admins."""
        return Set.objects.visible().filter(home_site=True)[:4]

    @staticmethod
    def get_expositions():
        """Return a list of promoted Exposition."""
        return Exposition.objects.live().filter(promoted_site=True)

    @staticmethod
    def get_allies():
        """Return a list of DataSources marked as allied."""
        return DataSource.objects.filter(is_ally=True)

    @staticmethod
    def get_promoted_resources():
        """Return a list of PromotedContentResource."""
        return PromotedContentResource.objects.visible()

    def get_context_data(self, **kwargs):
        """Extend context with required blocks and data for Home."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["based_on_reads"] = list(self.get_based_on_reads)
        context["most_read"] = list(self.get_most_read)
        context["collections"] = self.collections
        context["expositions"] = list(self.get_expositions())
        context["curated_collections"] = list(self.get_curated_collections())
        context["promoted_resources"] = list(self.get_promoted_resources())
        context["allies"] = list(self.get_allies())
        return context

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.
        If content resource sharing is cancelled shows a message.
        """
        if "cancelled" in request.GET:
            messages.success(self.request, _("No compartiste ningún recurso."))
            return HttpResponseRedirect(request.build_absolute_uri(request.path))
        self.collections_formset_object_list = list(self.collections)
        return super().get(request, *args, **kwargs)


class OverrideGetFieldChoices(GetFieldChoices):
    MODEL_FROM_FIELD = {
        "creatorequivalencerelation__contentresourceequivalence__equivalence__name": "creator",
        "creator__original_value": "creator",
        "subjectequivalencerelation__contentresourceequivalence__equivalence__name": "subject",
        "subject__original_value": "subject",
    }

    def get(self, request, model=None, field_name=None):
        if field_name in [
            "creatorequivalencerelation__contentresourceequivalence__equivalence__name",
            "subjectequivalencerelation__contentresourceequivalence__equivalence__name",
        ]:
            queryset = Equivalence.objects.filter(
                field=self.MODEL_FROM_FIELD[field_name]
            )
            if queryset.count() > int(
                os.environ.get("ADVANCED_FILTERS_MAX_CHOICES", 500)
            ):
                return JsonResponse({"results": []})
            return JsonResponse(
                {
                    "results": [
                        {"id": equivalence.name, "text": equivalence.name}
                        for equivalence in queryset.iterator()
                    ]
                }
            )

        if field_name in [
            "creator__original_value",
            "subject__original_value",
        ]:
            queryset = ContentResourceEquivalence.objects.filter(
                field=self.MODEL_FROM_FIELD[field_name]
            ).distinct()
            if queryset.count() > int(
                os.environ.get("ADVANCED_FILTERS_MAX_CHOICES", 500)
            ):
                return JsonResponse({"results": []})

            return JsonResponse(
                {
                    "results": [
                        {
                            "id": content_resource.original_value,
                            "text": content_resource.original_value,
                        }
                        for content_resource in queryset.iterator()
                    ]
                }
            )

        return super().get(request, model=model, field_name=field_name)
