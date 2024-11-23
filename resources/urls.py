"""Define urls for resources app."""
from django.conf import settings
from django.http import HttpResponse
from django.urls import path

from . import views

urlpatterns = []

# Loader.io verification view.
if "loaderio" in settings.SITE_VERIFICATIONS:
    LOADERIO_CODE = settings.SITE_VERIFICATIONS["loaderio"]
    urlpatterns.append(
        path(
            f"loaderio-{LOADERIO_CODE}.txt",
            lambda request: HttpResponse(f"loaderio-{LOADERIO_CODE}"),
            name="loaderio_verify",
        )
    )
