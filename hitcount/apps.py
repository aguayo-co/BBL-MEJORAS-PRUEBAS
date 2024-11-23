from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HitcountConfig(AppConfig):
    name = "hitcount"
    verbose_name = _("Contador de Clicks")
