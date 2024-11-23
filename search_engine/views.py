"""Define views for Search Engine app."""

from distutils.util import strtobool
from itertools import chain

from constance import config
from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from harvester.models import (
    CollaborativeCollection,
    Collection,
    ContentResource,
    ContentResourceEquivalence,
    DataSource,
    Equivalence,
    Set,
)
from harvester.views import CancellShareMessageMixin
from harvester.views_api import ApiSearchFiltersMixin, ApiSearchMixin
from resources.views import CollectionsGroupsFormsetMixin
from search_engine import config as es_conf
from search_engine.elasticsearch import get_didyoumean, get_suggestions, search

from .forms import SearchFormsMixin


class SearchView(
    CancellShareMessageMixin,
    ApiSearchMixin,
    SearchFormsMixin,
    CollectionsGroupsFormsetMixin,
    TemplateResponseMixin,
    ContextMixin,
    View,
):
    """
    List Collections, Resources or any searchable model.
    Search results are based on Filters and a Search Text.
    """

    paginate_by = None
    template_name = "harvester/search_result_list.html"
    matched_elements = None
    total_grouped_matches = 0
    total_matches = 0
    object_list = None
    current_page = 1
    didyoumean = None
    model = ContentResource

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE_SEARCH

    def get_context_data(self, **context):
        """Get the context for this view."""
        # Custom Paginator
        paginator = Paginator(range(0, self.total_grouped_matches), self.paginate_by)
        context.update(
            {
                "paginator": paginator,
                "page_obj": paginator.get_page(self.current_page),
                "is_paginated": paginator.num_pages > 1,
                "object_list": self.object_list or [],
                "didyoumean": self.didyoumean or [],
            }
        )

        if not self.object_list:
            context["most_popular"] = self.get_most_popular()

        context = super().get_context_data(**context)
        context["search_form"] = self.get_form()
        context["boolean_operator_formset"] = self.get_formset()
        self.request._has_search_form = True  # pylint: disable=protected-access
        return context

    def get(self, request, *args, **kwargs):
        """
        Proccess search params to get a ElasticSearch match response.

        Returns Json API response if requested.
        """
        search_form = self.get_form()
        boolean_operator_formset = self.get_formset()
        self.current_page = int(self.request.GET.get("page", 1))

        if "cancelled" in request.GET:
            messages.success(self.request, _("No compartiste ningún recurso."))
            return HttpResponseRedirect(request.build_absolute_uri(request.path))

        if self.validate_forms(form=search_form, formset=boolean_operator_formset):
            search_params = self.get_search_params(
                form=search_form, formset=boolean_operator_formset
            )
            (
                self.total_matches,
                self.total_grouped_matches,
                self.object_list,
            ) = self.get_search_results(self.model, search_params)

            self.total_grouped_matches = (
                self.total_grouped_matches["value"]
                if isinstance(self.total_grouped_matches, dict)
                else self.total_grouped_matches
            )
            self.total_matches = (
                self.total_matches["value"]
                if isinstance(self.total_matches, dict)
                else self.total_matches
            )

        if self.model._meta.model_name == "collection":
            self.collections_formset_object_list = self.object_list

        context = self.get_context_data(form=search_form)

        if self.api:
            return JsonResponse(self.get_api_context_data(context=context))

        return self.render_to_response(context)

    def get_collections_formset(self):
        """Get collections formset."""
        if self.model._meta.model_name == "collection":
            return super().get_collections_formset()
        return None

    @staticmethod
    def get_search_results(model, search_params):
        """Process search results."""
        search_results = search(model, **search_params)
        search_results["result_list_id"] = list(
            map(int, search_results["result_list_id"])
        )

        if model._meta.model_name == "collection":
            collections_id = []
            sets_id = []
            for index, result_id in enumerate(search_results["result_list_id"]):
                collection_type = search_results["result_list_collection_type"][index]
                if collection_type == "set":
                    sets_id.append(result_id)
                else:
                    collections_id.append(result_id)

            collection_queryset = (
                model.objects.filter(pk__in=collections_id).annotate_groups().all()
            )
            set_queryset = Set.objects.filter(pk__in=sets_id).annotate_groups().all()

            final_result_list = sorted(
                chain(collection_queryset, set_queryset),
                key=lambda result: search_results["result_list_id"].index(result.id),
            )
        else:
            queryset = model.objects.filter(pk__in=search_results["result_list_id"])

            unordered_results = queryset.all()

            final_result_list = sorted(
                unordered_results,
                key=lambda result: search_results["result_list_id"].index(result.id),
            )

        return (
            search_results["total_ungrouped_result"],
            search_results["total_grouped_result"],
            final_result_list,
        )

    @staticmethod
    def get_most_popular():
        """Return the 20 resources with most visits."""
        return (
            ContentResource.objects.visible()
            .filter(hitcount__isnull=False)
            .order_by("-hitcount__hits")[:20]
        )

    def get_search_params(self, form, formset=None):
        """Get search params to be used on Elastic search request."""
        if form.cleaned_data.get("content_model"):
            self.model = apps.get_model(form.cleaned_data.get("content_model"))

        search_params = {
            "search_text": form.cleaned_data.get("search_text") or None,
            "exact_search": form.cleaned_data.get("exact_search") or None,
            "filters": {
                k: v
                for k, v in form.cleaned_data.items()
                if v
                and k
                not in [
                    "search_text",
                    "order_by",
                    "content_model",
                    "content_type",
                    "from_publish_year",
                    "to_publish_year",
                ]
            },
            "from_publish_year": form.cleaned_data.get("from_publish_year"),
            "to_publish_year": form.cleaned_data.get("to_publish_year"),
        }
        search_params["filters"]["data_source_id_filter"] = None

        if formset and formset.is_bound:
            search_params.update({"boolean_queries": formset.cleaned_data})

        if form.cleaned_data.get("order_by"):
            search_params["order_by"] = form.cleaned_data.get("order_by")

        # Se hace cambio del nombre del filtro
        # para igualar el mapeo en índice de elasticsearch
        if form.cleaned_data.get("content_type"):
            search_params["filters"]["type_field_filter"] = form.cleaned_data.get(
                "content_type"
            )

        if form.cleaned_data.get("language"):
            search_params["filters"]["language_field_filter"] = form.cleaned_data.get(
                "language"
            )

        if form.cleaned_data.get("rights"):
            search_params["filters"]["rights_field_filter"] = form.cleaned_data.get(
                "rights"
            )

        if form.cleaned_data.get("subject"):
            search_params["filters"]["subject_field"] = form.cleaned_data.get("subject")

        # Obtener didyoumean si se ha hecho una búsqueda
        if search_params["search_text"]:
            didyoumean = get_didyoumean(self.model, search_params["search_text"])
            if didyoumean:
                if len(search_params["search_text"].strip().split()) > 1:
                    results = self.get_search_results(
                        self.model,
                        {"search_text": didyoumean[0]["text"], "exact_search": True},
                    )
                    if results[2] and results[2][0]:
                        self.didyoumean = results[2][0].title[0]
                else:
                    self.didyoumean = didyoumean[0]["text"]

        # Obtener valores finales para los filtros
        for name, _filter in search_params["filters"].items():
            if isinstance(_filter, QuerySet):

                # Equivalences
                if _filter.model is Equivalence:
                    search_params["filters"][name] = self.get_equivalence_filters(
                        self.model, _filter
                    )

                # Data Sources
                if _filter.model is DataSource:
                    search_params["filters"]["data_source_id_filter"] = [
                        ds.id for ds in search_params["filters"][name]
                    ]
                    search_params["filters"][name] = None

            # Online Resources
            if name == "data_source_online_resources":
                search_params["filters"][name] = [bool(strtobool(_filter))]

            # collection_set
            if name == "collection_set":
                search_params["filters"][name] = [_filter]

            # sets
            if name == "sets":
                search_params["filters"][name] = [_filter.pk]

            # collection type
            if name == "collection_type" and Collection._meta.model_name in _filter:
                search_params["filters"][name].append(
                    CollaborativeCollection._meta.model_name
                )

        # Limpiar filtros para enviar solo campos válidos
        search_params["filters"] = self.get_cleaned_filters(
            self.model, search_params["filters"]
        )

        search_params["pagination_size"] = self.paginate_by
        search_params["pagination_start"] = (
            self.current_page * self.paginate_by
        ) - self.paginate_by
        return search_params

    @staticmethod
    def get_equivalence_filters(model, equivalences):
        """
        Obtiene los valores de equivalencias.
        Estos valores serán enviados como filtros a elasticsearch.
        """
        if model is ContentResource:
            return list(
                ContentResourceEquivalence.objects.filter(
                    equivalence__in=equivalences
                ).values_list("original_value", flat=True)
            )
        return list(equivalences.values_list("pk", flat=True))

    @staticmethod
    def get_cleaned_filters(model, filters):
        """Envía solo filtros a elasticsearch que coincidan con los campos indexados."""
        if filters["data_source_id_filter"] is None:
            del filters["data_source_id_filter"]

        index_fields = es_conf.INDICES_CONFIG[es_conf.get_indice_name(model)][
            "mappings"
        ]["properties"]

        return {k: v for k, v in filters.items() if k in index_fields}


class SuggestionsView(View):
    """Return Suggestions for a search criteria."""

    def get(self, request):
        """Given a search text phrase returns suggestions."""
        search_text = request.GET.get("search_text")

        return JsonResponse(get_suggestions(search_text))


class SearchFiltersView(ApiSearchFiltersMixin, View):
    """Return the available search filters."""

    def get(self, request):
        """
        Handle Get Request.

        Returns Rest API response.
        """
        return JsonResponse(self.get_api_context_data())


class AdvancedSearchView(
    CancellShareMessageMixin,
    SearchFormsMixin,
    TemplateResponseMixin,
    ContextMixin,
    View,
):
    """Handle advance search."""

    template_name = "harvester/advanced_search.html"

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the search form."""
        data = self.request.GET.copy()
        data["content_model"] = self.form_class.MODEL_CHOICES[0][0]

        return {"data": data}

    def get_context_data(self, **kwargs):
        """Add search all forms to context."""
        context = super().get_context_data(**kwargs)
        context["search_form"] = self.get_form()
        context["boolean_operator_formset"] = self.get_formset()

        return context

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.

        Render the forms or send them to the search results page.
        """
        if "done" in self.request.GET:
            if self.validate_forms():
                dict_params = self.request.GET.copy()
                dict_params.pop("done")
                dict_params.update(
                    {"content_model": self.form_class.MODEL_CHOICES[0][0]}
                )
                url_params = dict_params.urlencode()
                base_url = reverse("search")
                url = f"{base_url}?{url_params}"
                return HttpResponseRedirect(url)

        if "cancelled" in request.GET:
            messages.success(self.request, _("No compartiste ningún recurso."))
            return HttpResponseRedirect(request.build_absolute_uri(request.path))

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class SearchUsersView(LoginRequiredMixin, View):
    """Return Suggestions for a search criteria."""

    def get(self, request):
        """Given a search text phrase returns suggestions."""
        search_text = request.GET.get("search_text")
        response = {}
        if search_text:
            User = get_user_model()
            users_queryset = User.objects.exclude(pk=self.request.user.pk)
            results_queryset = users_queryset.search(search_text)
            response = User.format_search_users_result_queryset(
                results_queryset, search_text
            )

        return JsonResponse(response)
