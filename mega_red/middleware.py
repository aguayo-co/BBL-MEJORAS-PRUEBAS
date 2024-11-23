"""Define middlewares for MegaRed app."""

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect, QueryDict
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _


def accept_terms_middleware(get_response):
    """Force user to Profile page if has not accepted terms and conditions."""

    def accepted_terms(user):
        """Check if user accepted terms."""
        profile = getattr(user, "profile", None)
        return profile and profile.accept_terms

    def is_allowed_page(request):
        """Check current page is allowed when user has not accepted terms."""
        resolved = resolve(request.path_info)
        return resolved.url_name in [
            "profile-edit",
            "logout",
        ] or resolved.route.startswith("__debug__")

    def middleware(request):
        """Redirect to profile edit if user has not accepted terms."""
        user = request.user
        if (
            user.is_authenticated
            and not accepted_terms(user)
            and not is_allowed_page(request)
        ):
            messages.warning(
                request,
                _(
                    "Tienes que aceptar los términos y condiciones"
                    " para navegar como usuario registrado."
                ),
            )
            query = QueryDict(mutable=True)
            query[REDIRECT_FIELD_NAME] = request.get_full_path()
            return HttpResponseRedirect(
                f"{reverse('profile-edit')}?{query.urlencode()}"
            )

        return get_response(request)

    return middleware
