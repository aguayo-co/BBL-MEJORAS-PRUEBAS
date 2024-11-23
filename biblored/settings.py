"""
Django settings for biblored project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import ipaddress
import os
import sys

import django_heroku
from import_export.formats import base_formats

from resources.embed_custom_provider import youtube_custom_provider

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG") == "True"
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"


# Application definition

INSTALLED_APPS = [
    # "instance_selector",
    "instance_selector.apps.AppConfig",
    # Resources app to allow template overrides.
    "resources.apps.ResourcesConfig",
    # Custom apps
    "mega_red.apps.MegaRedConfig",
    "custom_user.apps.CustomUserConfig",
    "harvester.apps.HarvesterConfig",
    "search_engine.apps.SearchEngineConfig",
    "expositions.apps.ExpositionsConfig",
    "hitcount.apps.HitcountConfig",
    "menus.apps.MenusConfig",
    # Priority Third party
    "django_select2",
    # WagTail Dependencies
    "wagtail_modeladmin",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.locales",
    "wagtail",
    "modelcluster",
    "taggit",
    "wagtailmodelchooser",
    "wagtailmenus",
    # "wagtail.contrib.postgres_search",
    # Third party
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.contrib.admindocs",
    "django.contrib.sites",
    "webpack_loader",
    "resources.apps.DBLoggingConfig",
    "simple_history",
    "django_q",
    "resources.apps.ConstanceConfig",
    "constance.backends.database",
    "formtools",
    "import_export",
    "gtm",
    "ckeditor",
    "resources.apps.AdvancedFiltersConfig",
    "gm2m",
    "wagtailcache",
    # Development apps.
    "debug_toolbar",
    "django_extensions",
    # Keep last so any app can override templates.
    "django.forms",
    # Hide apps of wagtail and taggit
    "hide_wagtail.apps.HideWagtailConfig",
]

SITE_ID = 1

# if sys.platform in ["darwin", "linux"]:
#     # Monitoring first!
#     # Scout seems not to be installable in windows.
#     INSTALLED_APPS.insert(0, "scout_apm.django")


MIDDLEWARE = [
    "django_brotli.middleware.BrotliMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "wagtailcache.cache.UpdateCacheMiddleware",
    "xff.middleware.XForwardedForMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "mega_red.middleware.accept_terms_middleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "wagtailcache.cache.FetchFromCacheMiddleware",
    "wagtail.contrib.legacy.sitemiddleware.SiteMiddleware",
]

ROOT_URLCONF = "biblored.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "builtins": ["resources.templatetags.builtins"],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtailmenus.context_processors.wagtailmenus",
                "resources.context_processors.global_context",
                "search_engine.context_processors.global_context",
                "harvester.context_proccessors.global_context",
            ],
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "biblored.wsgi.application"

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {"default": None}

if "DATABASE_URL" not in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DATABASE_NAME"],
            "USER": os.environ["DATABASE_USER"],
            "PASSWORD": os.environ["DATABASE_PASSWORD"],
            "HOST": os.environ["DATABASE_HOST"],
            "PORT": os.environ["DATABASE_PORT"],
            "DISABLE_SERVER_SIDE_CURSORS": os.environ.get(
                "DISABLE_SERVER_SIDE_CURSORS", "False"
            )
            == "True",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = "es-co"
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

TIME_ZONE = "America/Bogota"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Email
# https://docs.djangoproject.com/en/dev/topics/email/

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    EMAIL_PORT = os.environ["EMAIL_PORT"]
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS") == "True"

if "DEFAULT_FROM_EMAIL" in os.environ:
    DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]

if "SERVER_EMAIL" in os.environ:
    SERVER_EMAIL = os.environ["SERVER_EMAIL"]

# Upload Handler
FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]

# Webpack-Django integration
# https://github.com/owais/django-webpack-loader

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "wp/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
    }
}


# Custom User model
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
AUTH_USER_MODEL = "custom_user.User"

# Authentication backends model
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-authentication-backends
AUTHENTICATION_BACKENDS = [
    "mega_red.auth.MegaRedBackend",
    "django.contrib.auth.backends.ModelBackend",
    "custom_user.auth.SettingsBackend",
]
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
LOGOUT_REDIRECT_URL = "login"
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
# https://github.com/vintasoftware/safari-samesite-cookie-issue
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None


# Django Specific
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# Storage
DEFAULT_FILE_STORAGE = os.environ["DEFAULT_FILE_STORAGE"]
if DEFAULT_FILE_STORAGE == "storages.backends.s3boto3.S3Boto3Storage":
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_EXPIRE = 60 * 60 * 24 * 7 * 4  # 4 weeks
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
    AWS_S3_REGION_NAME = os.environ["AWS_S3_REGION_NAME"]
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": f"max-age={60 * 60 * 24 * 7 * 4}"  # 4 weeks
    }
    if "AWS_QUERYSTRING_AUTH" in os.environ:
        AWS_QUERYSTRING_AUTH = os.environ["AWS_QUERYSTRING_AUTH"] == "True"
    if "AWS_LOCATION" in os.environ:
        AWS_LOCATION = os.environ["AWS_LOCATION"].strip("/") + "/"

# Django-Q Queue Task
Q_CLUSTER = {
    "name": "biblored",
    "orm": "default",
    "label": "Tareas en segundo plano",
    "workers": int(os.environ.get("DJANGO_Q_WORKERS", "2")),
    "timeout": int(os.environ.get("DJANGO_Q_TIMEOUT", "1200")),
    "retry": int(os.environ.get("DJANGO_Q_RETRY", "1260")),
    "ack_failures": True,
    "catch_up": os.environ.get("DJANGO_Q_CATCH_UP", "False") == "True",
    "queue_limit": int(os.environ.get("DJANGO_Q_LIMIT", "2")),
    "sync": TESTING or os.environ.get("DJANGO_Q_SYNC", "False") == "True",
    "log_level": os.environ.get("LOG_LEVEL", "WARNING"),
    "recycle": int(os.environ.get("DJANGO_Q_RECYCLE", "500")),
    "django_redis": "default",
    "save_limit": 1000,
}
UNPARALLEL_TIMEOUT = Q_CLUSTER["timeout"]

# Constance
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_SUPERUSER_ONLY = os.environ.get("CONSTANCE_SUPERUSER_ONLY", "False") == "True"

CONSTANCE_CONFIG = {
    "EZPROXY_SERVER_URL": (
        "https://ezproxy.biblored.gov.co",
        "Url de acceso a EZProxy",
        str,
    ),
    "EZPROXY_SECRET": ("..BibloRed2018Proxy**", "Usuario de acceso a EZProxy", str),
    "TITLE": ("Biblored", "Titulo del Sitio", str),
    "LOGO_1": (None, "Url del LOGO Principal", "image_field"),
    "LOGO_2": (None, "Url del Logo Secundario", "image_field"),
    "HEADER_IMAGE": (None, "Url de la imagen del Hero", "image_field"),
    "HEADER_TEXT": (
        """[uno]
1 = "Más de"
2 = 25000
3 = "Libros"
[dos]
1 = "Cerca de"
2 = "3 millones de"
3 = "Datos"
""",
        "Opciones del texto cambiante, formato TOML",
        "toml_field",
    ),
    "PAGE_SIZE_SEARCH": (20, "Elementos por página en las búsquedas", int),
    "PAGE_SIZE": (10, "Elementos por página para otras páginas", int),
    "MEGARED_AUTH_URL": (
        "http://servicio.biblored.gov.co/servicios_var/afiliate/afiliacion/",
        "URL de servicio de autenticación de MegaRed.",
        str,
    ),
    "MEGARED_REGISTRATION_URL": (
        "https://www.biblored.gov.co/formulario-de-afiliacion/",
        "URL de registro de usuarios de MegaRed.",
        str,
    ),
    "ADMIN_NOTIFICATIONS_MESSAGE_DAYS": (
        "0",
        "Los números de los días de la semana (separados por comas) en los que los "
        "administradores recibirán una notificación con el recuento "
        "de las notificaciones de 7 días antes. "
        "Lunes es 0 y Domingo es 6",
        str,
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Opciones Generales": (
        "TITLE",
        "LOGO_1",
        "LOGO_2",
        "HEADER_IMAGE",
        "HEADER_TEXT",
        "PAGE_SIZE_SEARCH",
        "PAGE_SIZE",
        "ADMIN_NOTIFICATIONS_MESSAGE_DAYS",
    ),
    "Opciones de Autenticación": ("MEGARED_AUTH_URL", "MEGARED_REGISTRATION_URL"),
    "Opciones de EzProxy": ("EZPROXY_SERVER_URL", "EZPROXY_SECRET"),
}

CONSTANCE_ADDITIONAL_FIELDS = {
    "image_field": ["resources.fields.ImageField"],
    "toml_field": ["resources.fields.TomlField"],
}
CONSTANCE_UPLOAD_PATH = os.environ.get("CONSTANCE_UPLOAD_PATH", "constance/uploads/")


# https://www.fomfus.com/articles/how-to-use-ip-ranges-for-django-s-internal_ips-setting
class IpNetworks:
    """
    A Class that contains a list of IPvXNetwork objects.

    Credits to https://djangosnippets.org/snippets/1862/
    """

    networks = []

    def __init__(self, addresses):
        """Create a new IpNetwork object for each address provided."""
        for address in addresses:
            self.networks.append(ipaddress.ip_network(address))

    def __contains__(self, address):
        """Check if the given address is contained in any of our Networks."""
        for network in self.networks:
            if ipaddress.ip_address(address) in network:
                return True
        return False


if os.environ.get("INTERNAL_ADDRESSES"):
    INTERNAL_IPS = IpNetworks(os.environ["INTERNAL_ADDRESSES"].split(" "))


# Django Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "biblored.middleware.show_toolbar",
}

DEBUG_TOOLBAR_PANELS = (
    # "pympler.panels.MemoryPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
    # "template_profiler_panel.panels.template.TemplateProfilerPanel",
)

# Allowed domains
if os.environ.get("ALLOWED_HOSTS"):
    ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(" ")


# SSL Settings.
# Trust Proxy header and redirect to SSL.
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Use X-Forwarded-For header
# https://pypi.org/project/django-xff/
XFF_TRUSTED_PROXY_DEPTH = int(os.environ.get("XFF_TRUSTED_PROXY_DEPTH", "0"))


# Harvester Specific Settings
TASK_PAGE_LENGTH = int(os.environ.get("TASK_PAGE_LENGTH", "400"))
FAILED_TASK_ATTEMPTS = int(os.environ.get("FAILED_TASK_ATTEMPTS", "4"))


# Elastic configuration
# Append "API" to make it a HIDDEN_SETTINGS.
SEARCHBOX_SSL_URL_API = os.environ.get("SEARCHBOX_SSL_URL")


# Google Tag Manager
GOOGLE_TAG_ID = os.environ.get("GOOGLE_TAG_ID")


# tawk.to
TAWKTO_ID = os.environ.get("TAWKTO_ID")


# Site verifications
SITE_VERIFICATIONS = {}
if "SITE_VERIFICATIONS_LOADERIO" in os.environ:
    SITE_VERIFICATIONS["loaderio"] = os.environ["SITE_VERIFICATIONS_LOADERIO"]


# Limit for Background deletion task.
DELETE_BACKGROUND_LIMIT = int(os.environ.get("DELETE_BACKGROUND_LIMIT", "500"))
DELETE_BACKGROUND_MINUTES = int(os.environ.get("DELETE_BACKGROUND_MINUTES", "1"))


# Robots
# https://github.com/dabapps/django-simple-robots
ROBOTS_ALLOW_HOST = os.environ.get("ROBOTS_ALLOW_HOST", "")


#############
# HitCount  #
#############
# Multiple hits in this period will be counted only once
HITCOUNT_KEEP_HIT_ACTIVE = {
    "hours": int(os.environ.get("HITCOUNT_KEEP_HIT_ACTIVE_HOURS", "6"))
}

# Any hit older than this time will be removed
HITCOUNT_KEEP_HIT_IN_DATABASE = {
    "days": int(os.environ.get("HITCOUNT_KEEP_HIT_IN_DATABASE_DAYS", "30"))
}

# CKEditor (Wysiwyg)
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript"],
            ["NumberedList", "BulletedList", "-", "Outdent", "Indent", "-"],
            ["Link", "Unlink"],
            ["RemoveFormat"],
            ["Source"],
        ],
    }
}


# WagTail settings
WAGTAIL_SITE_NAME = "Biblored - Biblioteca Digital de Bogotá"

# Extra config to Atomic Rebuilds in Indexes
ATOMIC_REBUILD = os.environ.get("ATOMIC_REBUILD", "True") == "True"
INDEX_CHUNK_SIZE = int(os.environ.get("INDEX_CHUNK_SIZE", "50"))

WAGTAILSEARCH_TIMEOUT = os.environ.get("WAGTAILSEARCH_TIMEOUT", None)
WAGTAILSEARCH_MAX_RETRIES = os.environ.get("WAGTAILSEARCH_MAX_RETRIES", 10)
WAGTAILSEARCH_RETRY_ON_TIMEOUT = (
    os.environ.get("WAGTAILSEARCH_RETRY_ON_TIMEOUT", "True") == "True"
)

if os.environ.get("WAGTAILSEARCH_ELASTIC_URL"):
    WAGTAILSEARCH_BACKENDS = {
        "default": {
            "BACKEND": os.environ.get(
                "WAGTAILSEARCH_ELASTIC_BACKEND",
                "wagtail.search.backends.elasticsearch7",
            ),
            "URLS": [os.environ.get("WAGTAILSEARCH_ELASTIC_URL")],
            # "INDEX": "wagtail",
            "TIMEOUT": (
                int(WAGTAILSEARCH_TIMEOUT)
                if WAGTAILSEARCH_TIMEOUT is not None
                else None
            ),
            "ATOMIC_REBUILD": ATOMIC_REBUILD,
            "OPTIONS": {
                "max_retries": int(WAGTAILSEARCH_MAX_RETRIES),
                "retry_on_timeout": WAGTAILSEARCH_RETRY_ON_TIMEOUT,
            },
            "INDEX_SETTINGS": {
                "settings": {
                    "index": {
                        "number_of_shards": 1,
                    },
                    "analysis": {
                        "analyzer": {
                            "default": {
                                "type": "custom",
                                "tokenizer": "lowercase",
                                "filter": ["asciifolding", "suggestions_ngram"],
                            },
                            "suggestions": {
                                "type": "custom",
                                "tokenizer": "lowercase",
                                "filter": ["asciifolding", "suggestions_ngram"],
                            },
                            "lowercase-asciifolding": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "asciifolding"],
                            },
                        },
                        "normalizer": {
                            "lowercase": {
                                "type": "custom",
                                "filter": ["lowercase", "asciifolding"],
                            },
                        },
                        "filter": {
                            "lowercase": {"type": "lowercase"},
                            "suggestions_ngram": {
                                "type": "nGram",
                                "min_gram": 3,
                                "max_gram": 15,
                            },
                        },
                    },
                }
            },
        }
    }
else:
    WAGTAILSEARCH_BACKENDS = {
        "default": {
            "BACKEND": "wagtail.search.backends.database",
        }
    }

# Caches #
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "biblored_cache",
    },
}
if (
    os.environ.get("MEMCACHE_URL")
    and os.environ.get("MEMCACHE_PASS")
    and os.environ.get("MEMCACHE_USER")
):
    CACHES["default"] = {
        "BACKEND": "django_bmemcached.memcached.BMemcached",
        "LOCATION": os.environ.get("MEMCACHE_URL"),
        "OPTIONS": {
            "username": os.environ.get("MEMCACHE_USER"),
            "password": os.environ.get("MEMCACHE_PASS"),
        },
    }
# https://docs.wagtail.io/en/v2.9/advanced_topics/performance.html
if os.environ.get("REDIS_URL"):
    CACHES["pagecache"] = {
        "BACKEND": "wagtailcache.compat_backends.django_redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "bbl",
        "TIMEOUT": 3600,
    }
    CACHES["renditions"] = {
        "BACKEND": "wagtailcache.compat_backends.django_redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL"),
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "img",
        "TIMEOUT": 60 * 60 * 24 * 7 * 4,  # 4 weeks
    }
    CACHES["select2"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "sel2",
    }

WAGTAIL_CACHE = os.environ.get("WAGTAIL_CACHE", "True") == "True"
SELECT2_CACHE_BACKEND = os.environ.get("SELECT2_CACHE_BACKEND", "default")
CACHE_COUNT_TIMEOUT = 60
CACHE_EMPTY_QUERYSETS = True

# Configuration for iPython Notebook
# https://django-extensions.readthedocs.io/en/latest/shell_plus.html#ipython-notebook
NOTEBOOK_ARGUMENTS = ["--ip", "0.0.0.0", "--allow-root", "--no-browser"]

# Wagtail embeds
# WAGTAILEMBEDS_FINDERS = [
#     {
#         "class": "wagtail.embeds.finders.oembed",
#         "providers": [youtube_custom_provider],
#     }
# ]

# APM (Elastic)

ELASTIC_APM = {
    "SERVICE_NAME": os.environ.get("EAPM_SERVICE_NAME", "bbl-bdb-staging"),
    "SECRET_TOKEN": "15owSmVibPQ2wOQgq1",
    "SERVER_URL": "https://33072cdc17a04156b9c700472b54700f.apm.us-east-2.aws.elastic-cloud.com:443",
    "ENVIRONMENT": "production",
    "DJANGO_TRANSACTION_NAME_FROM_ROUTE": True,
    "DEBUG": True,
}

## Filtros Avanzados
ADVANCED_FILTERS_MAX_CHOICES = int(os.environ.get("ADVANCED_FILTERS_MAX_CHOICES", 500))

# Import / Export
IMPORT_EXPORT_CHUNK_SIZE = int(os.environ.get("IMPORT_EXPORT_CHUNK_SIZE", 50))
EXPORT_FORMATS = [base_formats.XLSX, base_formats.CSV]
IMPORT_EXPORT_SKIP_ADMIN_ACTION_EXPORT_UI = True

## Wagtail Menus
WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN = (
    os.environ.get("WAGTAILMENUS_FLAT_MENUS_EDITABLE_IN_WAGTAILADMIN", "False")
    == "True"
)

WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (
    ("first_top", "Primera Columna Superior"),
    ("first_bottom", "Primera Columna Inferior"),
    ("second_top", "Segunda Columna Superior"),
    ("second_bottom", "Segunda Columna Inferior"),
    ("third_top", "Tercera Columna Superior"),
    ("third_bottom", "Tercera Columna Inferior"),
)

WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME = "custom_flat_menu_items"
WAGTAIL_APPEND_SLASH = True

#########################################
# Heroku configuration                  #
#                                       #
# NO NEW settings below this point.     #
# Only extend Heroku settings.          #
#########################################

# Activate Django-Heroku.
django_heroku.settings(locals(), allowed_hosts=False)

# Logger Config
LOGGING["handlers"]["db_log"] = {  # pylint: disable=undefined-variable
    "level": "DEBUG",
    "class": "django_db_logger.db_log_handler.DatabaseLogHandler",
}
LOGGING["loggers"]["biblored"] = {  # pylint: disable=undefined-variable
    "handlers": ["db_log"],
    "level": "DEBUG",
}
LOGGING["loggers"][""] = {  # pylint: disable=undefined-variable
    "handlers": ["console"],
    "level": os.environ.get("LOG_LEVEL", "INFO"),
}
if "DB_LOG_LEVEL" in os.environ:
    LOGGING["loggers"]["django.db"] = {  # pylint: disable=undefined-variable
        "propagate": False,
        "handlers": ["console"],
        "level": os.environ["DB_LOG_LEVEL"],
    }

X_FRAME_OPTIONS = "SAMEORIGIN"
