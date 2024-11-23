"""Define urls for expositions app."""
from django.urls import include, path
from wagtail import urls as wagtail_urls

from . import views

app_name = "expositions"
urlpatterns = [
    path("expositions/", views.ExpositionListView.as_view(), name="list"),
    path("", include(wagtail_urls)),
]
