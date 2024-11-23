from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HarvesterConfig(AppConfig):
    name = "harvester"
    verbose_name = _("cosechador")
