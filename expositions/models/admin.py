"""Admin models for Wagtail."""

from wagtail_modeladmin.helpers import WagtailBackendSearchHandler
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from custom_user.models import User
from expositions.helpers import SelectAllButtonHelper
from expositions.models.map import MapMilestone
from expositions.models.timeline import TimelineMilestone
from expositions.views import MapMilestoneCreateView, TimelineMilestoneCreateView
from harvester.models import ContentResource, Equivalence


@modeladmin_register
class ContentResourceWagtailAdmin(ModelAdmin):
    """Wagtail Admin Model for Content Resource."""

    model = ContentResource
    add_to_settings_menu = False
    exclude_from_explorer = True
    button_helper_class = SelectAllButtonHelper
    list_filter = ("setandresource__set",)
    list_per_page = 10
    search_handler_class = WagtailBackendSearchHandler

    def get_queryset(self, request):
        """Limit Queryset for resources that exists."""
        qs = (
            super()
            .get_queryset(request)
            .filter(visible=True)
            .only("title", "pk", "data_source")
        )
        return qs


@modeladmin_register
class TypeEquivalenceWagtailAdmin(ModelAdmin):
    """Wagtail Admin Model for Type Equivalence."""

    model = Equivalence
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_per_page = 10
    search_handler_class = WagtailBackendSearchHandler

    def get_queryset(self, request):
        """Limit Queryset for resources that exists."""
        qs = super().get_queryset(request).filter(field="type")
        return qs


@modeladmin_register
class MapMilestoneWagtailAdmin(ModelAdmin):
    """Wagtail Admin Model for Map Milestone."""

    model = MapMilestone
    add_to_settings_menu = False
    exclude_from_explorer = True
    search_fields = ("title", "short_description", "place")
    create_view_class = MapMilestoneCreateView
    form_view_extra_js = ["wagtailadmin/js/map_milestone_create.js"]
    index_template_name = "modeladmin/index_map_milestone.html"


@modeladmin_register
class TimelineMilestoneWagtailAdmin(ModelAdmin):
    """Wagtail Admin Model for Map Milestone."""

    model = TimelineMilestone
    add_to_settings_menu = False
    exclude_from_explorer = True
    search_fields = ("title", "short_description", "place")
    create_view_class = TimelineMilestoneCreateView
    form_view_extra_js = ["wagtailadmin/js/timeline_milestone_create.js"]
    index_template_name = "modeladmin/index_timeline_milestone.html"


@modeladmin_register
class UserWagtailAdmin(ModelAdmin):
    """Wagtail Admin Model for User."""

    model = User
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_per_page = 10
    search_handler_class = WagtailBackendSearchHandler
