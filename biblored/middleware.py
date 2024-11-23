"""Define middlewares for Biblored."""
from django.conf import settings


def show_toolbar(request):
    """Determine if DEBUG_TOOLBAR should be shown."""
    if (
        request.META.get("REMOTE_ADDR", None) not in settings.INTERNAL_IPS
        or not settings.DEBUG
    ):
        return False

    return True
