"""Define admin interfaces for :model:`harvester.DataSource`."""

import os
import tempfile
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from django.core.files.storage import default_storage

from django.contrib import admin, messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.forms import CharField, ChoiceField, HiddenInput, IntegerField
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django_q.tasks import async_task
from formtools.wizard.views import SessionWizardView

from harvester.views import DynamicIdentifierSampleView, DynamicUrlRegexSampleView
from search_engine.functions.es_backend_helpers import mark_resources_for_reindex
from .actions import hide, show
from ..common import (
    DUBLIN_CORE_DEFAULT_ASSOCIATION,
    DUBLIN_CORE_DEFAULT_ASSOCIATION_INITIAL,
    MARC_XML_DEFAULT_ASSOCIATION_INITIAL,
)
from ..forms import forms
from ..forms.forms import DataSourceAdminForm, DynamicIdentifierConfigInlineForm
from ..functions.csv import get_csv_columns
from ..functions.harvester import (
    MAPPABLE_FIELDS,
    BadSource,
    download_file_and_upload,
    generate_file_name,
    get_harvested_sets,
    get_mapping,
    get_sets,
    get_storage_path,
    prepare_file,
    upload_to_storage,
)
from ..models import DataSource, DynamicIdentifierConfig, Schedule, ControlHarvestStatus


class ScheduleInline(admin.TabularInline):
    """Define inline admin for Schedules."""

    model = Schedule
    max_num = 8
    ordering = ("day",)


class DynamicIdentifierConfigInline(admin.StackedInline):
    """Define inline admin for Dynamic Identifier Config."""

    model = DynamicIdentifierConfig
    form = DynamicIdentifierConfigInlineForm
    template = "harvester/dynamic_identifier_stacked_inline.html"
    extra = 1
    ordering = ("id",)

    def has_add_permission(self, request, obj=None):
        """Check if can add new Dynamic Identifier Configs."""
        if obj and obj.has_expired_dynamic_identifiers():
            return False
        return super().has_add_permission(request, obj=obj)

    def has_change_permission(self, request, obj=None):
        """Check if can edit Dynamic Identifier Configs."""
        if obj and obj.has_expired_dynamic_identifiers():
            return False
        return super().has_change_permission(request, obj=obj)

    def has_delete_permission(self, request, obj=None):
        """Check if can delete new Dynamic Identifier Configs."""
        if obj and obj.has_expired_dynamic_identifiers():
            return False
        return super().has_delete_permission(request, obj=obj)


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    """Integrate DataSource with admin."""

    actions = [hide, show]
    inlines = [ScheduleInline, DynamicIdentifierConfigInline]
    list_display = [
        "name",
        "sets",
        "exclusive",
        "datasource_actions",
        "updated_at",
        "created_at",
    ]
    list_filter = ["updated_at", "exclusive"]
    readonly_fields = ["data_mapping"]
    search_fields = ["name"]
    form = DataSourceAdminForm

    def save_related(self, request, form, formsets, change):
        """
        Save related models.

        Expire ContentResources when a DynamicIdentifierConfig is modified.
        """
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            if formset.queryset and isinstance(
                formset.queryset[0], DynamicIdentifierConfig
            ):
                if (
                    formset.deleted_objects
                    or formset.changed_objects
                    or formset.new_objects
                ):
                    async_task(
                        "harvester.helpers.set_dynamic_identifier_expired_task",
                        formset.instance,
                    )
                    formset.instance.contentresource_set.update(
                        dynamic_identifier_expired=True
                    )
                    break

    def get_queryset(self, request):
        """Augment queryset to include Sets count."""
        queryset = super().get_queryset(request)
        return queryset.annotate(Count("set"))

    def sets(self, obj):
        """Return set count for an object."""
        return obj.set__count

    sets.admin_order_field = "set__count"

    def get_urls(self):
        """Return admin urls."""
        urls = super().get_urls()
        more_urls = [
            path(
                "<int:pk>/harvest",
                self.admin_site.admin_view(
                    NewHarvestWizardView.as_view(
                        condition_dict={
                            "0": NewHarvestWizardView.has_upload_method,
                            "1": NewHarvestWizardView.has_csv_format,
                            "2": NewHarvestWizardView.has_dublin_core_format,
                            "3": NewHarvestWizardView.has_marc_format,
                            "5": NewHarvestWizardView.can_select_sets,
                        }
                    )
                ),
                name="harvest",
            ),
            path(
                "<int:pk>/mark_resources_for_reindex",
                self.admin_site.admin_view(MarkDataSourceForReindexView.as_view()),
                name="mark_resources_for_reindex",
            ),
            path(
                "<int:pk>/dynamic_url_regex_sample/",
                self.admin_site.admin_view(DynamicUrlRegexSampleView.as_view()),
                name="dynamic_url_regex_sample",
            ),
            path(
                "<int:pk>/dynamic_identifier_regex_sample/",
                self.admin_site.admin_view(DynamicIdentifierSampleView.as_view()),
                name="dynamic_identifier_regex_sample",
            ),
        ]
        return more_urls + urls

    def datasource_actions(self, obj):
        """Send an actions to the view/controller to start datasources processes."""
        # Start the Harvesting process/Wizard
        harvest_link = '<a href="{}" class="button">{}</a>'.format(
            reverse("admin:harvest", args=[obj.id]), _("cosechar")
        )

        return mark_safe(harvest_link)

    datasource_actions.short_description = _("acciones")


class NewHarvestWizardView(PermissionRequiredMixin, SessionWizardView):
    """Harvest Wizard form with steps."""

    permission_required = ["harvester.can_harvest"]
    template_name = "harvester/harvest_wizard.html"
    data_source = None
    storage_path = ""
    file_path = ""
    form_list = [
        forms.UploadFileForm,  # 0
        forms.MappingAbstractForm,  # 1 <- CsvMappingForm
        forms.MappingAbstractForm,  # 2 <- DublinCoreMappingForm
        forms.MappingAbstractForm,  # 3 <- MarcMappingForm
        forms.MappingAbstractForm,  # 4 <- PositionMappingForm
        forms.SelectSetsForm,  # 5
        forms.ConfirmHarvestForm,  # 6
    ]
    file_storage = default_storage

    def setup(self, request, *args, **kwargs):
        """Initialize view attributes."""
        super().setup(request, *args, **kwargs)
        self.data_source = DataSource.objects.get(pk=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        """Verify that the source can be harvested (has no expired identifiers)."""
        if self.data_source.has_expired_dynamic_identifiers():
            messages.add_message(
                self.request,
                messages.WARNING,
                _(
                    'No se puede cosechar "%(fuente)s": Contiene Identificadores'
                    " en proceso de actualización. Intente nuevamente más tarde."
                )
                % {"fuente": self.data_source.name},
            )
            return HttpResponseRedirect(
                reverse("admin:harvester_datasource_changelist")
            )
        return super().dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        """Process the form and creates a task when finished."""
        # Update Mapping
        self.data_source.data_mapping = get_mapping(form_list)
        self.data_source.save()

        # Get Sets
        selected_sets = get_selected_sets(form_list)

        if selected_sets is None:
            selected_sets = get_sets(self.data_source)

        # Get Task ID
        group_id = self.storage.extra_data["group_id"]

        # Upload File
        temp_file_path = self.get_temp_file_path(form_list)
        if temp_file_path:
            extension = os.path.splitext(temp_file_path)[1]
            self.storage_path = os.path.join(
                get_storage_path(self.data_source.id, group_id),
                generate_file_name(extension),
            )
            default_storage.save(
                self.storage_path, default_storage.open(temp_file_path)
            )

        async_task(
            "harvester.functions.harvester.harvest_task",
            self.data_source,
            selected_sets,
            group_id,
            self.storage_path,
            self.request.user,
            task_name=_("Cosechamiento: %(source)s [%(group_id)s]")
            % {"source": self.data_source.name[:40], "group_id": group_id},
            group=group_id,
        )
        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Tarea de cosechamiento creada correctamente"),
        )
        if not self.data_source.config["method"] == "api":
            harvest_stage = ControlHarvestStatus(
                data_source=self.data_source, group_id=group_id, user=self.request.user, stage=0, status=0
            )
            harvest_stage.create_stage_first_time()
        return HttpResponseRedirect(reverse("admin:harvester_datasource_changelist"))

    def get_context_data(self, form, **kwargs):
        """Initialize the form context with usable data as step titles."""
        context = super().get_context_data(form=form, **kwargs)
        # Specific Step Modification if required
        if self.steps.current == "0":
            context.update({"title": _("subir archivo")})
        if self.steps.current == "1":
            context.update({"title": _("mapeo por CSV")})
        if self.steps.current == "2":
            context.update({"title": _("mapeo por Dublin Core")})
        if self.steps.current == "3":
            context.update({"title": _("mapeo por Marc")})
        if self.steps.current == "4":
            context.update({"title": _("posición Item Principal")})
        if self.steps.current == "5":
            context.update({"title": _("selecciona Sets")})
        if self.steps.current == "6":  # Confirmation Screen
            context.update({"title": _("confirmar")})
        return context

    def get_form(self, step=None, data=None, files=None):
        """Given a step this method obtains and returns an associated Form instance."""
        form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current

        # Specific Form Modification based on steps
        if step == "1":
            if data:
                columns = self.storage.extra_data["columns"]
            else:
                if not self.storage.current_step_files == None:
                    file_pointer = self.storage.current_step_files["0-file_field"]
                elif self.data_source.config["url"]:
                    file_path = download_file_and_upload(
                        self.data_source.config["url"],
                        self.data_source,
                        self.storage.extra_data["group_id"],
                        self.request.user
                    )[0]
                    file_pointer = prepare_file(file_path)
                columns, invalid_columns = get_csv_columns(
                    file_pointer,
                    self.data_source.config["delimiter"],
                    self.data_source.config["quotechar"],
                )
                if invalid_columns:
                    messages.add_message(
                        self.request,
                        messages.ERROR,
                        _(
                            "Las siguientes columnas tienen nombres inválidos:"
                            " '%(columns)s'."
                        )
                        % {"columns": "', '".join(invalid_columns)},
                    )

                self.storage.extra_data["columns"] = columns
            form.fields.update(get_csv_mapping_fields(columns))
            form.initial = self.get_form_initial(step)
        if step == "2":
            form.fields.update(get_dublin_core_mapping_fields())
        if step == "3":
            form.fields.update(get_marc_mapping_fields())
        if step == "4":
            form.fields.update(get_position_mapping_fields())
        if step == "5":
            try:
                form.fields["sets"].choices = get_sets(self.data_source)
            except BadSource:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    _(
                        "No fue posible conseguir la lista de Sets."
                        " Revise la configuración de la fuente."
                    ),
                )
        if step == "6":
            for prev_step in ["1", "2", "3"]:
                prev_data = self.storage.data["step_data"].get(prev_step, None) or {}
                for key, value in prev_data.items():
                    clean_key = key.replace(f"{prev_step}-", "")
                    clean_val = value[0]
                    if clean_val and (
                        clean_val in MAPPABLE_FIELDS or clean_key in MAPPABLE_FIELDS
                    ):
                        field = CharField(
                            disabled=True, initial=clean_val, required=False
                        )
                        form.fields.update({clean_key.capitalize(): field})

        return form

    def get_form_initial(self, step):
        """Return the initial data for a form given a step."""
        initial_data = super().get_form_initial(step)

        try:
            self.storage.extra_data["group_id"]
        except KeyError:
            self.storage.extra_data["group_id"] = str(uuid.uuid1())

        initial_data["group_id"] = self.storage.extra_data["group_id"]

        # File Path
        if step == "1":
            initial_data["file_path"] = self.file_path
            if self.data_source.data_mapping:
                for model_field, columns in self.data_source.data_mapping.items():
                    if model_field in MAPPABLE_FIELDS:
                        for column in columns:
                            initial_data[column] = model_field

        # Mapping for dublincore
        if step == "2":
            initial_data.update(
                {
                    key: value[0]
                    for key, value in self.data_source.data_mapping.items()
                    if key in MAPPABLE_FIELDS
                }
                if self.data_source.data_mapping
                else DUBLIN_CORE_DEFAULT_ASSOCIATION_INITIAL
            )

        # Mapping for marc
        if step == "3":
            initial_data.update(
                {
                    key: value[0]
                    for key, value in self.data_source.data_mapping.items()
                    if key in MAPPABLE_FIELDS
                }
                if self.data_source.data_mapping
                else MARC_XML_DEFAULT_ASSOCIATION_INITIAL
            )

        # Mapping for positions
        if step == "4" and self.data_source.data_mapping:
            initial_data.update(
                {
                    f"position_{key}": value + 1
                    for key, value in self.data_source.data_mapping["positions"].items()
                    if key in MAPPABLE_FIELDS
                }
                if "positions" in self.data_source.data_mapping
                else {}
            )

        # Add Common Elements to Initial #
        # Sets
        if step and "sets" in self.form_list[step].base_fields:
            initial_data["sets"] = list(
                get_harvested_sets(DataSource.objects.get(pk=self.kwargs["pk"]))
            )

        # Data Source
        if step and "data_source" in self.form_list[step].base_fields:
            initial_data["data_source"] = self.data_source

        return initial_data

    def get_form_step_files(self, form):
        """Look inside a form to obtain the uploaded files in it."""
        for file in form.files.values():
            form.cleaned_data["file_path"] = file.temporary_file_path()
            self.file_path = file.temporary_file_path()
        return form.files

    @staticmethod
    def get_temp_file_path(form_list):
        """Return the temporary location of an uploaded file."""
        for form in form_list:
            if "file_field" in form.cleaned_data:
                return form.cleaned_data["file_field"].file.name
        return None

    def get_temp_file(self):
        """Return an uploaded file as a File like object."""
        for file in self.request.FILES.values():
            return file.file
        return None

    # Conditional Functions
    def has_upload_method(self):
        """Check if the datasource method is upload."""
        if self.data_source.config["method"] == "upload":
            return True
        return False

    def can_select_sets(self):
        """Check if the datasource allows to select sets."""
        if self.data_source.config["method"] == "api":
            return True
        return False

    def has_csv_format(self):
        """Check if the datasource format is a csv file."""
        if self.data_source.config["format"] in ["csv", "txt", "tsv"]:
            return True
        return False

    def has_dublin_core_format(self):
        """Check if the datasource format is dublincore."""
        if self.data_source.config["format"] in ["oai_dc"]:
            return True
        return False

    def has_marc_format(self):
        """Check if the datasource method is marc21."""
        if self.data_source.config["format"] in ["marc_xml", "marc_plain"]:
            return True
        return False


class MarkDataSourceForReindexView(PermissionRequiredMixin, DetailView):
    """Mark for reindex to resources from the selected data source."""

    permission_required = ["harvester.can_reindex_datasource"]
    model = DataSource
    template_name = "harvester/admin/mark_datasource_for_reindex_confirm.html"

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """POST method."""
        instance = self.get_object()
        queryset = instance.contentresource_set.all()
        mark_resources_for_reindex(queryset)
        info = instance._meta.app_label, instance._meta.model_name
        return redirect(reverse("admin:%s_%s_changelist" % info))


def get_dublin_core_mapping_fields():
    """Return a list of mappable fields for a dublin core datasource instance."""
    form_fields = {}
    empty_choice = [("", _("Selecciona una opción"))]
    required_fields = ["title", "identifier"]

    for m_field in MAPPABLE_FIELDS:
        required = m_field in required_fields

        form_fields[m_field] = ChoiceField(
            label=_(m_field),
            choices=empty_choice + DUBLIN_CORE_DEFAULT_ASSOCIATION,
            required=required,
        )

    return form_fields


def get_marc_mapping_fields():
    """Return a list of mappable fields for a marc21 datasource instance."""
    form_fields = {}
    required_fields = ["title", "identifier"]

    for m_field in MAPPABLE_FIELDS:
        required = m_field in required_fields

        form_fields[m_field] = CharField(
            label=_(m_field),
            required=required,
            help_text=_(
                "Escriba la posición a mapear para Marc21: field$subfield$ind1$ind2$"
            ),
        )
    return form_fields


def get_csv_mapping_fields(columns):
    """Return a list of mappable fields for a csv datasource based on file columns."""
    form_fields = {}
    empty_choice = [("", _("Selecciona una opción"))]
    model_choices = [(model_field, model_field) for model_field in MAPPABLE_FIELDS]

    for file_field in columns:
        form_fields[file_field] = ChoiceField(
            label=file_field, choices=empty_choice + model_choices, required=False
        )
    form_fields["csv_mapping"] = CharField(required=False, widget=HiddenInput())
    return form_fields


def get_selected_sets(validated_form_list):
    """Return a list of selected sets suitable for iterate over inside the task."""
    selected_sets = None
    for form in validated_form_list:
        if "sets" in form.cleaned_data:
            selected_sets = [
                (spec, name)
                for spec, name in form.fields["sets"].choices
                if spec in form.cleaned_data["sets"]
            ]
    return selected_sets


def get_position_mapping_fields():
    """Return a list of mappable fields to select the Principal Item Position."""
    form_fields = {}
    for m_field in MAPPABLE_FIELDS:
        form_fields[f"position_{m_field}"] = IntegerField(
            label=_(m_field),
            required=True,
            help_text=_("Seleccione la posición que se usará como Item Principal"),
            min_value=1,
            initial=1,
        )
    return form_fields
