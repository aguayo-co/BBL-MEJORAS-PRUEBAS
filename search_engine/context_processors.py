"""Context preprocessors for Harvester app."""
from .forms import SearchForm


def global_context(request):
    """Include search form globally."""
    context = {}
    if not hasattr(request, "_has_search_form"):
        context["search_form"] = SearchForm(auto_id="id_search_form_%s")
    return context
