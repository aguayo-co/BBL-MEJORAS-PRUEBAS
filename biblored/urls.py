"""
biblored URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
"""

from debug_toolbar.middleware import get_show_toolbar
from django.conf import settings, urls
from django.contrib import admin
from django.urls import include, path, re_path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView

from harvester.views import ServeHumansView, ServeRobotsView
from resources.views import OverrideGetFieldChoices

urlpatterns = [
    path("documents/", include(wagtaildocs_urls)),
    re_path(
        r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$",
        ServeView.as_view(action="redirect"),
        name="wagtailimages_serve",
    ),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("wagtail/", include(wagtailadmin_urls)),
    path("wagtail/pages/", include(wagtail_urls)),
    path("", include("search_engine.urls")),
    path("", include("harvester.urls")),
    path("", include("resources.urls")),
    path("accounts/", include("mega_red.urls")),
    path("robots.txt", ServeRobotsView.as_view()),
    path("humans.txt", ServeHumansView.as_view(), name="humans"),
    path(
        r"^advanced_filters/field_choices/(?P<model>.+)/(?P<field_name>.+)/?",
        OverrideGetFieldChoices.as_view(),
        name="afilters_get_field_choices",
    ),
    path(
        r"^advanced_filters/field_choices/$",
        OverrideGetFieldChoices.as_view(),
        name="afilters_get_field_choices",
    ),
    path("", include("expositions.urls")),
]

if get_show_toolbar():
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

if settings.DEBUG:
    urlpatterns = [
        path("__400__/", lambda request: urls.handler400(request, Exception())),
        path("__403__/", lambda request: urls.handler403(request, Exception())),
        path("__404__/", lambda request: urls.handler404(request, Exception())),
        path("__500__/", urls.handler500),
    ] + urlpatterns
