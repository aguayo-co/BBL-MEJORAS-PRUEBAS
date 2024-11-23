"""Define form widgets for Harvester app."""

from django.forms import MultiWidget, RadioSelect, Select, TextInput, URLInput
from django.utils.translation import gettext_lazy as _

from harvester.common import DUBLIN_CORE_DEFAULT_ASSOCIATION


class BaseMultiWidget(MultiWidget):
    """Basic Implementation for MultiWidget."""

    template_name = None
    fields = None

    def decompress(self, value):
        """Split the compressed value into pieces for each widget."""
        if value and isinstance(value, (dict, list)):
            return [value.get(key, None) for key in self.fields]
        return [None] * len(self.fields)


class DataSourceConfigWidget(BaseMultiWidget):
    """Custom widget with a subset of subwidgets for a Data Source Configuration."""

    template_name = "harvester/data_source_config_widget.html"

    def __init__(self, methods, formats, json_fields, attrs=None):
        """Initialize the widget with a set of subwidgets."""
        _attrs = {"class": "data_source_config_widget"}
        self.fields = json_fields
        widgets = (
            RadioSelect(choices=methods, attrs={"data_label": self.fields["method"]}),
            Select(
                choices=((None, _("Seleccione un Formato")),) + formats,
                attrs={"data_label": self.fields["format"], "required": True},
            ),
            URLInput(attrs={"data_label": self.fields["url"], "required": True}),
            TextInput(attrs={"data_label": self.fields["delimiter"], "required": True}),
            TextInput(attrs={"data_label": self.fields["quotechar"], "required": True}),
        )
        if attrs:
            _attrs.update(**attrs)
        super().__init__(widgets=widgets, attrs=_attrs)

    class Media:
        """Meta attributes for widget."""

        css = {"all": ("harvester/css/data_source_config_widget_styles.css",)}
        js = ("harvester/js/data_source_config_widget.js",)


class DynamicUrlWidget(BaseMultiWidget):
    """Custom widget with a subset of subwidgets for a Dynamic Url Configuration."""

    template_name = "harvester/dynamic_url_widget.html"

    def __init__(self, json_fields, attrs=None):
        """Initialize the widget with a set of subwidgets."""
        _attrs = {"class": "dynamic_url_widget"}
        self.fields = json_fields
        widgets = (
            # Field
            Select(
                choices=((None, _("Seleccione un Campo")),)
                + tuple(DUBLIN_CORE_DEFAULT_ASSOCIATION),
                attrs={"data_label": self.fields["field"][0], "required": False},
            ),
            # Capture
            TextInput(
                attrs={
                    "data_label": self.fields["capture_expression"][0],
                    "required": True,
                    "help_text": self.fields["capture_expression"][1],
                }
            ),
            # Replace
            TextInput(
                attrs={
                    "data_label": self.fields["replace_expression"][0],
                    "required": True,
                    "help_text": self.fields["replace_expression"][1],
                }
            ),
        )
        if attrs:
            _attrs.update(**attrs)
        super().__init__(widgets=widgets, attrs=_attrs)

    class Media:
        """Meta attributes for widget."""

        css = {"all": ("harvester/css/dynamic_url_widget.css",)}
        js = ("harvester/js/dynamic_url_widget.js",)


class CaptureExpressionWidget(BaseMultiWidget):
    """Custom widget with a subset of subwidgets for a Data Source Configuration."""

    # TODO CAMBIAR
    template_name = "harvester/capture_expression_widget.html"
    CAPTURE_ACTIONS = ()

    def __init__(self, capture_actions, json_fields, attrs=None):
        """Initialize the widget with a set of subwidgets."""
        _attrs = {"class": "capture_expression_widget"}
        self.fields = json_fields
        self.CAPTURE_ACTIONS = capture_actions
        widgets = (
            Select(
                choices=capture_actions,
                attrs={
                    "data_label": self.fields["capture_expression"],
                    "required": True,
                },
            ),
            TextInput(
                attrs={
                    "data_label": self.fields["custom_capture_expression"],
                    "required": False,
                }
            ),
        )
        if attrs:
            _attrs.update(**attrs)
        super().__init__(widgets=widgets, attrs=_attrs)

    def decompress(self, value):
        """Split the compressed value into pieces for each widget."""
        decompressed_value = [None, None]
        print("VALUE", value)
        if value is not None:
            if isinstance(value, str):
                print("VALUE IS STRING")
                if value in [choice[0] for choice in self.CAPTURE_ACTIONS]:
                    decompressed_value[0] = value
                else:
                    decompressed_value[0] = "custom"
                    decompressed_value[1] = value
            else:
                decompressed_value[0] = value["capture_expression"]
                decompressed_value[1] = value["custom_capture_expression"]
        print("DECOMPRESSED VALUE", decompressed_value)
        return decompressed_value

    class Media:
        """Meta attributes for widget."""

        # TODO CAMBIAR
        css = {"all": ("harvester/css/data_source_config_widget_styles.css",)}
        js = ("harvester/js/capture_expression_widget.js",)
