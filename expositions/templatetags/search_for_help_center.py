from django import template

from expositions.models.pages import HelpCenterPage

register = template.Library()


@register.filter()
def search_for_help_center(page):
    """Search for the help center page in the current page's ancestors."""
    if page.get_children().type(HelpCenterPage).live().exists():
        return True
    return False
