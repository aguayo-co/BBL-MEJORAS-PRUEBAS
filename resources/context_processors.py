"""Context processor for Resources app."""
from constance import config
from django.core.files.storage import default_storage
from tomlkit import parse
from tomlkit.exceptions import TOMLKitError

from harvester.models import Equivalence


def global_context(request):
    """Extend context with global values."""
    # Skip in Wagtail Instance Selector
    try:
        if request.resolver_match.view_name in [
            "wagtail_instance_selector_embed",
            "harvester_contentresource_modeladmin_index",
        ]:
            return {}
    except AttributeError:
        # is a Preview
        pass

    try:
        header_text = parse(config.HEADER_TEXT)
    except TOMLKitError:
        header_text = None

    # Avoid duplicate queries to DB.
    logo_1 = config.LOGO_1
    logo_2 = config.LOGO_2
    header_image = config.HEADER_IMAGE

    context = {
        "title": config.TITLE,
        "logo_1": default_storage.url(logo_1) if logo_1 else None,
        "logo_2": default_storage.url(logo_2) if logo_2 else None,
        "header_image": (default_storage.url(header_image) if header_image else None),
        "header_text": header_text,
        "content_types": list(Equivalence.objects.filter(field="type")),
        "registration_url": config.MEGARED_REGISTRATION_URL,
    }
    return context
