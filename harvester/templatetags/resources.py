"""Template tags for Harvester app."""
from django import template

from ..models import ContentResource

register = template.Library()


@register.simple_tag(takes_context=True)
def get_resource_cite(context, processed_data):
    """Return citation with the URL placeholder replaced."""
    citation, url = processed_data.citation
    return citation % context.request.build_absolute_uri(url)


@register.simple_tag(takes_context=True)
def get_resource_external_url(context, processed_data):
    """Get the URL that redirects the user to a resource's external URL."""
    if isinstance(processed_data, ContentResource):
        processed_data = processed_data.processed_data

    url_data = processed_data.url_processor(context["user"])
    if url_data:
        return f"{processed_data.get_absolute_url()}?external"

    return None


@register.simple_tag()
def get_cancel_invitation_url(url):
    if "?" in url:
        return url + "&cancelled=True"
    return url + "?cancelled=True"
