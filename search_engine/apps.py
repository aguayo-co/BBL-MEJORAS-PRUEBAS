from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SearchEngineConfig(AppConfig):
    name = "search_engine"
    verbose_name = _("Buscador")
