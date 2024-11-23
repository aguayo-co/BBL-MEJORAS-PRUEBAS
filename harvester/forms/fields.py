"""Define form fields for Harvester app."""

import re

from django.core.validators import URLValidator
from django.forms import (
    CharField,
    ChoiceField,
    MultiValueField,
    URLField,
    ValidationError,
    Select,
)
from django.forms.models import ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from harvester.common import DUBLIN_CORE_DEFAULT_ASSOCIATION
from harvester.forms.widgets import (
    DataSourceConfigWidget,
    DynamicUrlWidget,
    CaptureExpressionWidget,
)

from ..models import Equivalence


class EquivalenceMultipleChoiceField(ModelMultipleChoiceField):
    """Form field for Equivalence model limited by its `field` value."""

    def __init__(self, field, **kwargs):
        """Set queryset limited by the value of `field`."""
        queryset = Equivalence.objects.filter(field=field).order_by("priority")
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj):
        """Return the name of the object."""
        return str(obj.name).capitalize()


class BaseMultiValueField(MultiValueField):
    """Base field to store multiple values in a JsonField."""

    json_fields = None

    default_error_messages = {
        "invalid": _("Ha ingresado un valor invalido."),
        "incomplete": _("Este campo es obligatorio."),
    }
    widget = None

    def list_to_dict(self, data_list):
        """Convert the data list to dict mapping fields to values."""
        return {field: data_list[index] for index, field in enumerate(self.json_fields)}

    def compress(self, data_list):
        """Convert the list of data to a dict if data exists."""
        if data_list:
            return self.list_to_dict(data_list)
        return None

    def bound_data(self, data, initial):
        """Convert the received data to a dict if not disabled."""
        if self.disabled:
            return initial

        return self.list_to_dict(data)


class DataSourceConfigField(BaseMultiValueField):
    """Custom widget for Data Source Config in Admin."""

    json_fields = {
        "method": _("Método"),
        "format": _("Formato"),
        "url": _("Url Api/Archivo"),
        "delimiter": _("Separador de Columnas"),
        "quotechar": _("Calificador de Texto"),
    }
    METHODS = (
        ("upload", _("Carga de Archivo")),
        ("url", _("Descarga desde URL")),
        ("api", _("Api OAI-PMH")),
    )
    FORMATS = (
        ("csv", _("Archivo Separado por Comas")),
        ("marc_xml", _("Marc21 XML")),
        ("marc_plain", _("Marc21 MRC/Plano")),
        ("oai_dc", _("Dublin Core")),
    )
    # For validations
    # Make sure these are in sync with widget JS.
    METHOD_VALID_FORMATS = {
        "upload": ["csv", "marc_xml", "marc_plain"],
        "url": ["csv", "marc_xml", "marc_plain"],
        "api": ["oai_dc"],
    }
    METHOD_REQUIRED_FIELDS = {
        "upload": ["format"],
        "url": ["format", "url"],
        "api": ["format", "url"],
    }
    FORMAT_REQUIRED_FIELDS = {
        "csv": ["delimiter", "quotechar"],
        "marc_xml": [],
        "marc_plain": [],
        "oai_dc": [],
    }
    widget = DataSourceConfigWidget(
        methods=METHODS, formats=FORMATS, json_fields=json_fields
    )

    def __init__(self, **kwargs):
        """Set the field list and his attrs."""
        fields = [
            ChoiceField(choices=self.METHODS),
            ChoiceField(choices=self.FORMATS),
            URLField(required=False),
            CharField(required=False, max_length=1),
            CharField(required=False, max_length=1),
        ]
        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def validate(self, value):
        """Run Validations for each field."""
        errors = []
        if value["format"] not in self.METHOD_VALID_FORMATS[value["method"]]:
            errors.append(
                ValidationError(
                    _("No es un Formato válido para el Método seleccionado"),
                    code="invalid",
                )
            )

        # Url
        if "url" in self.METHOD_REQUIRED_FIELDS[value["method"]] and not value["url"]:
            errors.append(
                ValidationError(_("Debe escribir una URL Válida"), code="invalid")
            )

        # Delimiter & Quotechar
        for field in self.FORMAT_REQUIRED_FIELDS[value["format"]]:
            if not value.get(field, None):
                errors.append(
                    ValidationError(
                        _("Se requiere un %(field)s para el formato %(format)s "),
                        params={
                            "field": self.json_fields[field],
                            "format": dict(self.FORMATS)[value["format"]],
                        },
                        code="incomplete",
                    )
                )

        if errors:
            raise ValidationError(errors)
        return super().validate(value)


class DynamicUrlField(BaseMultiValueField):
    """Custom widget for Dynamic Url in Datasource Admin."""

    json_fields = {
        "field": (_("Campo"), ""),
        "capture_expression": (
            _("Expresión de Captura"),
            _(
                "Usa una <a href='http://www.regular-expressions.info'>expresión"
                " regular</a>. Los grupos de captura podrán ser usados en la expresión"
                " de reemplazo."
            ),
        ),
        "replace_expression": (
            _("Expresión de Reemplazo"),
            _(
                "Crea el patrón de URL usando los grupos de captura de la expresión"
                " regular. Ejemplo: https://www.example.com/images/$1.jpg"
            ),
        ),
    }

    widget = DynamicUrlWidget(json_fields=json_fields)

    def __init__(self, **kwargs):
        """Set the field list and his attrs."""
        fields = [
            ChoiceField(choices=DUBLIN_CORE_DEFAULT_ASSOCIATION, required=False),
            CharField(),
            CharField(),
        ]
        super().__init__(fields=fields, **kwargs)

    def validate(self, value):
        """Run Validations for each field."""
        errors = []
        if not value["field"]:
            errors.append(
                ValidationError(_("Debe Seleccionar un campo"), code="incomplete")
            )

        try:
            re.compile(value["capture_expression"])
        except re.error:
            errors.append(
                ValidationError(
                    _("Debe escribir una Expresión Regular válida"), code="invalid"
                )
            )

        try:
            URLValidator()(str(value["replace_expression"]))
        except ValidationError:
            errors.append(
                ValidationError(_("Debe escribir una URL válida"), code="invalid")
            )

        if errors:
            raise ValidationError(errors)
        return super().validate(value)

    def clean(self, value):
        """Set the default value if no value is provided."""
        if value == ["", None, None]:
            return {}
        return super().clean(value)


class CaptureExpressionField(BaseMultiValueField):
    """Custom widget for Dynamic Identifier in Admin."""

    CAPTURE_ACTION_CHOICES = (
        (None, _("Seleccione")),
        (r"([0-9]+)", _("Capturar caracteres numéricos (0-9)")),
        (r"([a-zA-Z\s]+)", _("Capturar caracteres alfabéticos (a-z/A-Z)")),
        (r"([\w ]+)", _("Capturar caracteres alfanuméricos (a-z/A-Z/0-9)")),
        ("custom", _("Capturar utilizando una expresión regular personalizada")),
    )
    json_fields = {
        "capture_expression": _("Acción de Captura"),
        "custom_capture_expression": _("Expresión de Captura Personalizada"),
    }
    widget = CaptureExpressionWidget(
        capture_actions=CAPTURE_ACTION_CHOICES, json_fields=json_fields
    )

    def __init__(self, **kwargs):
        """Set the field list and his attrs."""
        fields = [
            ChoiceField(choices=self.CAPTURE_ACTION_CHOICES),
            CharField(required=False, max_length=255),
        ]
        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        """Convert the list of data to a dict if data exists."""
        compressed = super().compress(data_list)
        if compressed["capture_expression"] == "custom":
            compressed["capture_expression"] = compressed["custom_capture_expression"]
        return compressed["capture_expression"]

    def validate(self, value):
        """Run Validations for each field."""
        errors = []

        if value == "custom" and not value["custom_capture_expression"]:
            errors.append(
                ValidationError(
                    _("Debe escribir una expresión de captura personalizada"),
                    code="invalid",
                )
            )
        if errors:
            raise ValidationError(errors)
        return super().validate(value)


class CollectionsGroupsField(ModelMultipleChoiceField):
    """Collections group field custom validation."""

    user = None

    def clean(self, value):
        value = self.prepare_value(value)
        if self.required and not value:
            raise ValidationError(self.error_messages["required"], code="required")
        elif not self.required and not value:
            return self.queryset.none()
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages["list"], code="list")

        for index, group in enumerate(value):
            splitted_group = group.split("__name=")
            group_is_new = (
                len(splitted_group) == 2 and splitted_group[0] == "new_option"
            )
            if group_is_new:
                group_name = splitted_group[1]
                new_group = self.queryset.model.objects.get_or_create(
                    title=group_name, owner=self.user
                )
                value[index] = new_group[0].pk

        value = set([int(pk) for pk in value])
        qs = self._check_values(value)
        # Since this overrides the inherited ModelChoiceField.clean
        # we run custom validators here
        self.run_validators(value)
        return qs
