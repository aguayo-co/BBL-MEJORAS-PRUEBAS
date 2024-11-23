from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResourcesConfig(AppConfig):
    name = "resources"
    verbose_name = _("Recursos")


class AdvancedFiltersConfig(AppConfig):
    name = "advanced_filters"
    verbose_name = _("Filtros Avanzados")


class ConstanceConfig(AppConfig):
    name = "constance"
    verbose_name = _("Configuración general")


class DBLoggingConfig(AppConfig):
    name = "django_db_logger"
    verbose_name = _("Registros inicios de sesión")
