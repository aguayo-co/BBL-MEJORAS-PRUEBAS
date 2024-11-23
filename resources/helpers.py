"""Helper functions to be used accross the whole app."""
import base64
from urllib.parse import unquote, urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.urls import Resolver404, resolve


class ParallelCallsNotAllowed(Exception):
    """Raised when the a function is already running on another process."""

    def __init__(self, function):
        self.message = f"Se ha detenido la ejecución de esta tarea pues ya se está ejecutando una instancia anterior ({function})."
        super().__init__(self.message)

    def __str__(self):
        return self.message


def unparallel(_func=None, *, timeout=settings.UNPARALLEL_TIMEOUT):
    """
    Decorate a function to make sure it is not executed in parallel.

    Control execution with a cached flag.
    A shared cache backend is required. In memory cache or file cache will not work.
    """

    def unparallel_decorator(func):

        function = ".".join([func.__module__, func.__qualname__])
        cache_key = ".".join(["unparallel:", function])

        def police(*args, **kwargs):

            if cache.get(cache_key):
                raise ParallelCallsNotAllowed(function)

            cache.set(cache_key, True, timeout)
            value = func(*args, **kwargs)
            cache.delete(cache_key)
            return value

        return police

    if _func:
        # This allows for optional arguments for decorator.
        # If a function was received, return the decorated function.
        return unparallel_decorator(_func)

    return unparallel_decorator


def get_resolved_referer(request):
    """Get the resolved referer for the request."""
    referer = request.META.get("HTTP_REFERER", None)
    referer = referer and unquote(referer)
    if not referer:
        return None

    url_path = urlparse(referer)[2]

    # Remove settings.FORCE_SCRIPT_NAME from url if one exists.
    if settings.FORCE_SCRIPT_NAME and url_path.startswith(settings.FORCE_SCRIPT_NAME):
        url_path = url_path[len(settings.FORCE_SCRIPT_NAME) :]

    try:
        return resolve(url_path)
    except Resolver404:
        return None


def base64_file(data, name=None):
    _format, _img_str = data.split(";base64,")
    _name, ext = _format.split("/")
    if not name:
        name = _name.split(":")[-1]
    _img_str += "=" * (-len(_img_str) % 4)
    return ContentFile(base64.b64decode(_img_str), name="{}.{}".format(name, ext))
