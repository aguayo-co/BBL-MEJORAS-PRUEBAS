"""Define WagTail hooks for resources app."""

from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_global_admin_css")
def editor_css():
    """Include custom CSS for editing pages."""
    return format_html(
        '<link rel="stylesheet" href="{}">', static("wagtailadmin/edit/biblored.css")
    )


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Add custom CSS for admin interface."""
    return format_html(
        '<link rel="stylesheet" href="{}">', static("wagtailadmin/css/ag_core.css")
    )


@hooks.register("insert_editor_js")
def editor_css():
    """Include custom JS for editing pages."""
    return format_html(
        '<script src="{}"></script>', static("wagtailadmin/edit/charcount.js")
    )
