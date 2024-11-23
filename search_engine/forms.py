"""Define Forms for Search Engine app."""

from django import forms
from django.utils.translation import gettext_lazy as _

from expositions.models.pages import Exposition
from harvester.forms.fields import EquivalenceMultipleChoiceField
from harvester.forms.forms import ONLINE_RESOURCES_CHOICES
from harvester.models import Collection, ContentResource, DataSource, Set


class SearchForm(forms.Form):
    """Define a search and filter form."""

    MODEL_CHOICES = [
        (
            f"{model._meta.app_label}.{model._meta.model_name}",
            model._meta.verbose_name_plural,
        )
        for model in [ContentResource, Collection, Exposition]
    ]
    COLLECTION_TYPE_CHOICES = [
        (Set._meta.model_name, _("Colecciones institucionales")),
        (Collection._meta.model_name, _("Colecciones de usuario")),
    ]
    ORDER_BY_CHOICES = [
        (None, _("--")),
        ("recent", _("Más reciente")),
        ("-recent", _("Menos reciente")),
        ("az", _("De la A a la Z")),
        ("za", _("De la Z a la A")),
    ]
    search_text = forms.CharField(
        label=_("Actualmente estás buscando"),
        min_length=3,
        required=False,
        initial=None,
        widget=forms.CharField.widget(
            attrs={
                "autocomplete": "off",
                "placeholder": _("Actualmente estás buscando"),
            }
        ),
    )
    collection_type = forms.MultipleChoiceField(
        label=_("Tipo de colección"),
        choices=COLLECTION_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    content_model = forms.ChoiceField(
        label=_("Grupos de contenidos"),
        choices=MODEL_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )
    content_type = EquivalenceMultipleChoiceField(
        label=_("Tipo de contenido"),
        field="type",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    data_source_online_resources = forms.ChoiceField(
        label=_("Disponibilidad"),
        choices=ONLINE_RESOURCES_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )
    language = EquivalenceMultipleChoiceField(
        label=_("Idioma"),
        field="language",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    # TODO Recomiendo usar esto con typeahead
    data_sources = forms.ModelMultipleChoiceField(
        label=_("Fuente"), required=False, queryset=DataSource.objects.all()
    )
    rights = EquivalenceMultipleChoiceField(
        label=_("Licencia"),
        field="rights",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    subject = EquivalenceMultipleChoiceField(
        label=_("Tema"), field="subject", required=False
    )
    order_by = forms.ChoiceField(
        label=_("Ordenar por"), required=False, choices=ORDER_BY_CHOICES
    )
    exact_search = forms.BooleanField(label=_("Búsqueda exacta"), required=False)
    collection_set = forms.IntegerField(
        label=_("Colección de Usuario"),
        required=False,
    )
    # TODO Recomiendo usar esto con typeahead
    sets = forms.ModelChoiceField(
        label=_("Colección Institucional"),
        required=False,
        queryset=Set.objects,
    )
    from_publish_year = forms.IntegerField(
        label=_("Desde"),
        min_value=1000,
        required=False,
        widget=forms.widgets.NumberInput(attrs={"autocomplete": "off"}),
        error_messages={"min_value": _("Ingresar un número de más de 3 caracteres")},
    )
    to_publish_year = forms.IntegerField(
        label=_("Hasta"),
        min_value=1000,
        required=False,
        widget=forms.widgets.NumberInput(attrs={"autocomplete": "off"}),
        error_messages={"min_value": _("Ingresar un número de más de 3 caracteres")},
    )


class BooleanOperatorForm(forms.Form):
    """Boolean operator form."""

    OPERATOR_CHOICES = [("and", _("Y")), ("not", _("Y SIN"))]
    FIELD_CHOICES = [
        ("creator_field", _("Autor")),
        ("description", _("Description")),
        ("publisher", _("Publicador")),
        ("subject_field", _("Tema")),
        ("title", _("Título")),
    ]
    operator = forms.ChoiceField(
        label=_("Operador"),
        choices=OPERATOR_CHOICES,
        widget=forms.Select,
        required=False,
    )
    field = forms.ChoiceField(
        label=_("Selecciona por"),
        choices=FIELD_CHOICES,
        widget=forms.Select,
        required=False,
    )
    q = forms.CharField(
        label=_("Actualmente estás buscando"),
        min_length=3,
        required=False,
        initial=None,
        widget=forms.CharField.widget(
            attrs={"autocomplete": "off", "placeholder": _("¿Qué estás buscando?")}
        ),
    )
    is_or = forms.BooleanField(label="o", required=False)


class SearchFormsMixin:
    """Provide a way to show and handle the search forms."""

    form_class = SearchForm
    formset_form_class = BooleanOperatorForm
    formset_prefix = "boolean_operator"
    formset_management_fields = None

    def get_form(self):
        """Return an instance of the form to be used in this view."""
        return self.form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        data = self.request.GET.copy()
        if not data.get("content_model"):
            data["content_model"] = self.form_class.MODEL_CHOICES[0][0]

        return {"data": data}

    def get_formset_kwargs(self):
        """Return the keyword arguments for instantiating the formset."""
        return {"prefix": self.formset_prefix, "data": self.get_formset_data()}

    def get_formset(self):
        """Return an instance of the formset to be used in this view."""
        formset_class = forms.formset_factory(self.formset_form_class)

        return formset_class(**self.get_formset_kwargs())

    def get_formset_data(self):
        """Return the data parameter for instantiating the formset."""
        query_dict = self.request.GET
        required_fields = self.get_required_management_fields()
        has_required_fields = all([key in query_dict.keys() for key in required_fields])
        if has_required_fields:
            return self.request.GET.copy()

        return None

    def get_required_management_fields(self):
        """Return the formset required management fields."""
        return [
            f"{self.formset_prefix}-TOTAL_FORMS",
            f"{self.formset_prefix}-INITIAL_FORMS",
        ]

    def validate_form(self, form=None):
        """Validate form."""
        if form is None:
            form = self.get_form()
        return form.is_valid()

    def validate_formset(self, formset=None):
        """Validate formset."""
        if formset is None:
            formset = self.get_formset()
        if formset.is_bound:
            return formset.is_valid()
        return True

    def validate_forms(self, form=None, formset=None):
        """Validate all forms."""
        if self.validate_form(form) and self.validate_formset(formset):
            return True
        return False


class SearchFormWithInitialFilterBaseMixin:
    """Mixin for use search form with filter in model detail page."""

    def get_search_form_with_initial_filter_initial(self, field_name):
        initial = {
            field_name: self.get_object().pk,
        }
        return initial

    def get_search_form_with_initial_filter_kwargs(self, field_name):
        kwargs = {
            "initial": self.get_search_form_with_initial_filter_initial(field_name),
        }
        return kwargs

    def get_search_form_with_initial_filter(self, field_name):
        return SearchForm(**self.get_search_form_with_initial_filter_kwargs(field_name))


class SearchFormWithCollectionFilterMixin(SearchFormWithInitialFilterBaseMixin):
    """Mixin for use search form with collection filter in collection's detail page."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "search_form_with_collection_filter": self.get_search_form_with_initial_filter(  # noqa: E501
                    "collection_set"
                )
            }
        )
        return context


class SearchFormWithSetFilterMixin(SearchFormWithInitialFilterBaseMixin):
    """Mixin for use search form with set filter in set's detail page."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "search_form_with_set_filter": self.get_search_form_with_initial_filter(  # noqa: E501
                    "sets"
                )
            }
        )
        return context
