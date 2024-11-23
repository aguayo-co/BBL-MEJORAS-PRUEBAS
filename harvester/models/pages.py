from django.db.models import Case, When
from django.utils.functional import cached_property

from wagtail.admin.views.generic import InspectView, IndexView
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Harvest, StageHarvest


class HarvestHistoryIndexView(IndexView):

    def order_queryset(self, queryset):
        queryset = super().order_queryset(queryset)
        queryset = queryset.annotate(
            status_order=Case(
                When(status=1, then=1),
                When(status=0, then=2),
                When(status=3, then=3),
                When(status=2, then=4),
            )
        ).order_by('status_order', '-end_date')
        return queryset

    @cached_property
    def add_url(self):
        return None

    def get_edit_url(self, instance):
        return None


class HarvestHistoryInspectView(InspectView):
    def get_edit_url(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'stages': self.stages,
            'progress_bar_percent': self.progress_bar_percent
        })
        return context

    @property
    def stages(self):
        return StageHarvest.objects.filter(harvest__pk=self.pk).order_by('start_date')

    @property
    def progress_bar_percent(self):
        return int((self.object.progress_count/self.object.counter_total_resources) * 100)


class HarvestControl(ModelViewSet):
    model = Harvest
    form_fields = ["user"]
    icon = "history"
    add_to_admin_menu = False
    copy_view_enabled = False
    inspect_view_enabled = True
    inspect_view_class = HarvestHistoryInspectView
    index_view_class = HarvestHistoryIndexView
    template_prefix = "harvester/"
    list_display = [
        'get_data_source_name', 'user', 'stage',
        'get_status_display', 'start_date', 'end_date',
        'get_progress_count', 'remaining_time'
    ]
    list_filter = ['stage__stage', 'status', 'data_source_name']
    list_export = ['get_data_source_name', 'user',
                   'stage', 'get_status_display', 'start_date', 'end_date']
    search_fields = ['data_source_name']


harvest_control_viewset = HarvestControl("harvest-control")
