"""Context preprocessors for Harvester app."""
from harvester.models import CollectionsGroup


def global_context(request):
    """Include user's favorites collections group globally."""
    context = {}
    if not request.user.is_anonymous:
        object_instance, created = CollectionsGroup.objects.get_or_create(
            title="favoritos", owner=request.user
        )
        context["collections_favorites_group"] = object_instance.pk
    return context
