"""Define URLs for Harvester app."""
from django.shortcuts import redirect
from django.urls import include, path

from . import views
from .views_api import (
    CollectionsGroupCollectionFavoritesApiView,
    CollectionsGroupCollectionUpdateApiView,
    SharedResourcesApiView,
    ValidateFileApiView,
)

resources_patterns = [  # pylint: disable=invalid-name
    path("", lambda request: redirect("search"), name="content_resources"),
    path(
        "<int:pk>/", views.ContentResourceDetailView.as_view(), name="content_resource"
    ),
    path(
        "<int:pk>/availability/",
        views.ContentResourceDetailView.as_view(template_name_suffix="_availability"),
        name="content_resource_availability",
    ),
    path(
        "<int:pk>/collections/",
        views.ContentResourceCollectionsFormView.as_view(),
        name="content_resource_collections_edit",
    ),
    path(
        "<int:pk>/share/",
        views.ShareContentResourceFormView.as_view(),
        name="share_resource",
    ),
]

reviews_patterns = [  # pylint: disable=invalid-name
    path("", views.MyReviewListView.as_view(), name="my_reviews"),
    path("add", views.ReviewAddView.as_view(), name="review_add"),
    path("<int:pk>/edit", views.ReviewEditView.as_view(), name="review_edit"),
]

collections_patterns = [  # pylint: disable=invalid-name
    path("", views.CollectionListView.as_view(), name="collections"),
    path("my", views.MyCollectionListView.as_view(), name="my_collections"),
    path(
        "collaborative/",
        views.CollaborativeCollectionListView.as_view(),
        name="collaborative_collections",
    ),
    path(
        "collaborative/my",
        views.MyCollaborativeCollectionListView.as_view(),
        name="my_collaborative_collections",
    ),
    path("add/", views.CollectionAddView.as_view(), name="collection_add"),
    path("<int:pk>/", views.CollectionDetailView.as_view(), name="collection"),
    path("<int:pk>/edit/", views.CollectionEditView.as_view(), name="collection_edit"),
    path(
        "<int:pk>/invite/",
        views.CollectionCollaboratorsFormView.as_view(),
        name="collection_invite",
    ),
]

sets_patterns = [  # pylint: disable=invalid-name
    path("", views.SetListView.as_view(), name="sets"),
    path("<int:pk>/", views.SetDetailView.as_view(), name="set"),
]

collections_groups_patterns = [  # pylint: disable=invalid-name
    path("", views.CollectionsGroupListView.as_view(), name="collectionsgroups"),
    path("add/", views.CollectionsGroupAddView.as_view(), name="collectionsgroup_add"),
    path(
        "<int:pk>/", views.CollectionsGroupDetailView.as_view(), name="collectionsgroup"
    ),
    path(
        "favorites/",
        views.CollectionsGroupDetailView.as_view(favorites=True),
        name="collectionsgroup_favorites",
    ),
    path(
        "<int:pk>/edit/",
        views.CollectionsGroupEditView.as_view(),
        name="collectionsgroup_edit",
    ),
]

api_patterns = [  # pylint: disable=invalid-name
    path(
        "resources/<int:pk>/",
        views.ContentResourceDetailView.as_view(api="api_content_resource"),
        name="api_content_resource",
    ),
    path(
        "resources/<int:pk>/reviews/",
        views.ContentResourceDetailView.as_view(api="api_content_resource_reviews"),
        name="api_content_resource_reviews",
    ),
    path(
        "collections/<int:pk>/",
        views.CollectionDetailView.as_view(api="api_collection"),
        name="api_collection",
    ),
    path(
        "collections/<int:pk>/collaborators/",
        views.CollectionDetailView.as_view(api="api_collection_collaborators"),
        name="api_collection_collaborators",
    ),
    path(
        "collections/<int:pk>/resources/",
        views.CollectionDetailView.as_view(api="api_collection_resources"),
        name="api_collection_resources",
    ),
    path(
        "collections/<int:pk>/favorites-group/",
        CollectionsGroupCollectionFavoritesApiView.as_view(),
        name="api_collections_favorites_group",
    ),
    path(
        "collections/<int:pk>/add-to-groups/",
        CollectionsGroupCollectionUpdateApiView.as_view(),
        name="api_collections_add_to_groups",
    ),
    path(
        "shared-resources/<int:pk>/<str:method>/",
        SharedResourcesApiView.as_view(),
        name="api_shared_resource",
    ),
    path(
        "file-exist",
        ValidateFileApiView.as_view(),
        name="api_validate_exit",
    ),
]

urlpatterns = [
    path("resources/", include(resources_patterns)),
    path("reviews/", include(reviews_patterns)),
    path("collections/", include(collections_patterns)),
    path("collectionsgroups/", include(collections_groups_patterns)),
    path("sets/", include(sets_patterns)),
    path("api/", include(api_patterns)),
    path("select2/", include("django_select2.urls")),
]
