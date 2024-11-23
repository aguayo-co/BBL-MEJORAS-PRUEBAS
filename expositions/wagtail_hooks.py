"""Define WagTail hooks for expositions app."""

from django.http import Http404

from expositions.viewsets import content_resource_viewset, type_equivalence_viewset, subject_equivalence_viewset, \
    user_viewset
from wagtail import hooks



@hooks.register("before_serve_page")
def limit_expositions_path(page, request, args, kwargs):
    """
    Force pages from expositions to use the namespaced expositions urls.

    PagesWagtail pages for the models defined in this app should only be served
    through prefixed urls of this app.
    This is enforced in this hook.
    If a page from this module is being served outside of this app´s url,
    it should be considered a 404.
    """
    if (
        page._meta.app_label == "expositions"
        and request.resolver_match.app_name != "expositions"
    ):
        raise Http404


@hooks.register("construct_main_menu")
def hide_menu_items(request, menu_items):
    """Hide certain registered items in the main menu."""
    items_to_hide = [
        "recursos-de-contenido",
        "hitos-de-mapa",
        "hitos-de-linea-de-tiempo",
        "equivalencias",
        "usuarios",
    ]
    menu_items[:] = [item for item in menu_items if item.name not in items_to_hide]


@hooks.register("register_admin_viewset")
def register_resource_viewset():
    """Register the Resource Viewset for Custom Choosers."""
    return content_resource_viewset


@hooks.register("register_admin_viewset")
def register_type_equivalence_viewset():
    """Register the TypeEquivalence Viewset for Custom Choosers."""
    return type_equivalence_viewset


@hooks.register("register_admin_viewset")
def register_subject_equivalence_viewset():
    """Register the SubjectEquivalence Viewset for Custom Choosers."""
    return subject_equivalence_viewset


@hooks.register("register_admin_viewset")
def register_user_viewset():
    """Register the User Viewset for Custom Choosers."""
    return user_viewset

