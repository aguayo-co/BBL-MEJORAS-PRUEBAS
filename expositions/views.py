"""Define views for Expositions app."""

from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from wagtail.admin import messages
from wagtail_modeladmin.views import CreateView

from constance import config
from expositions.models import Exposition
from resources.views import FilteringMixin, OrderingMixin

from . import forms


class ExpositionListView(FilteringMixin, OrderingMixin, ListView):
    """List Collaborative Collections."""

    model = Exposition
    queryset = model.objects.live()
    ordering_options = {
        "az": (_("De la a A a la Z"), ["title"]),
        "za": (_("De la Z a la A"), ["-title"]),
        "recent": (_("Más reciente"), ["-last_published_at"]),
        "-recent": (_("Menos reciente"), ["last_published_at"]),
    }
    filters_form_class = forms.ExpositionFilters

    def setup(self, request, *args, **kwargs):
        """Set paginate_by property."""
        super().setup(request, *args, **kwargs)
        self.paginate_by = config.PAGE_SIZE

    def get_queryset(self):
        """Return the filtered queryset."""
        return self.filter_queryset(super().get_queryset())

    def get_promoted(self):
        """Return promoted elements with promoted_section."""
        return self.queryset.filter(promoted_section=True)

    def get_context_data(self, **kwargs):
        """Get the context for this view."""
        context = super().get_context_data(**kwargs)
        context["promoted"] = self.get_promoted()
        return context


class AjaxResponseMixin:
    """Mixin to add AJAX support to a form."""

    def form_invalid(self, form):
        """Handle invalid form."""
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return response

    def form_valid(self, form):
        """Handle valid form."""
        instance = form.save()
        messages.success(
            self.request,
            self.get_success_message(instance),
            buttons=self.get_success_message_buttons(instance),
        )
        if self.request.is_ajax():
            data = {
                "pk": instance.pk,
                "title": instance.title,
                "url": self.url_helper.get_action_url("edit", instance.pk),
            }
            return JsonResponse(data)
        return redirect(self.get_success_url())


class MapMilestoneCreateView(AjaxResponseMixin, CreateView):
    """Create a Map Milestone, assing the ParentalKey Map."""

    map = None

    def setup(self, request, *args, **kwargs):
        """Set map property."""
        self.map = request.GET.get("map", None)
        super().setup(request, *args, **kwargs)

    def get_initial(self):
        """Set Initial Form Data."""
        initial = super().get_initial()
        initial.update({"map": self.map})
        return initial


class TimelineMilestoneCreateView(AjaxResponseMixin, CreateView):
    """Create a Map Milestone, assing the ParentalKey Map."""

    timeline = None

    def setup(self, request, *args, **kwargs):
        """Set map property."""
        self.timeline = request.GET.get("timeline", None)
        super().setup(request, *args, **kwargs)

    def get_initial(self):
        """Set Initial Form Data."""
        initial = super().get_initial()
        initial.update({"timeline": self.timeline})
        return initial
