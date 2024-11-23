"""Define URLs for Harvester app."""
from django.urls import include, path

from . import views

search_patterns = [  # pylint: disable=invalid-name
    path("", views.SearchView.as_view(), name="search"),
    path("advanced/", views.AdvancedSearchView.as_view(), name="advanced_search"),
    path("suggestions/", views.SuggestionsView.as_view(), name="search_suggestions"),
    path("users/", views.SearchUsersView.as_view(), name="search_users"),
]

api_patterns = [  # pylint: disable=invalid-name
    path("search/", views.SearchView.as_view(api="api_search"), name="api_search"),
    path(
        "search/filters/",
        views.SearchFiltersView.as_view(api="api_search_filters"),
        name="api_search_filters",
    ),
]

urlpatterns = [
    path("search/", include(search_patterns)),
    path("api/", include(api_patterns)),
]
