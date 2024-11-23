"""Helpers for wagtail models, widgets or modules."""

from django.utils.translation import gettext_lazy as _
from wagtail_modeladmin.helpers import ButtonHelper


class SelectAllButtonHelper(ButtonHelper):
    """Provide the Select All Button for ModelAdmin Models."""

    def add_button(self, **__):
        """Replace the add button with one to select all."""
        custom_classnames = [
            "button",
            "bicolor",
            "icon",
            "icon-pick",
            "select_all_visible",
        ]
        classname = self.finalise_classname(custom_classnames)
        return {
            "url": None,
            "label": _("Seleccionar Todos Los %s") % self.verbose_name_plural,
            "classname": classname,
            "title": _("Seleccionar Todos Los %s") % self.verbose_name_plural,
        }
