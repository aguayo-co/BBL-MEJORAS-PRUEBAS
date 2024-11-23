"""Define urls for mega_red app."""

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [  # pylint: disable=invalid-name
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", views.MegaRedLoginView.as_view(), name="login"),
    path(
        "profile/",
        views.MegaRedProfileWithInvitationsView.as_view(),
        name="profile",
    ),
    path(
        "profile/<int:pk>/",
        views.MegaRedAnotherUserProfileView.as_view(),
        name="user-profile",
    ),
    path("profile/edit/", views.MegaRedProfileEditView.as_view(), name="profile-edit"),
    path(
        "profile/notifications/",
        views.NotificationsView.as_view(),
        name="notifications",
    ),
    path(
        "profile/<int:pk>/invitations",
        views.MegaRedProfileWithInvitationsView.as_view(),
        name="user-profile-invitations",
    ),
    path(
        "profile/<int:pk>/invitations",
        views.MegaRedProfileWithRequestsView.as_view(),
        name="user-profile-requests",
    ),
    path(
        "profile/invitations",
        views.MegaRedProfileWithInvitationsView.as_view(),
        name="profile-invitations",
    ),
    path(
        "profile/requests",
        views.MegaRedProfileWithRequestsView.as_view(),
        name="profile-requests",
    ),
    path(
        "profile/<int:pk>/shared-resources",
        views.MegaRedProfileWithSharedResourcesView.as_view(),
        name="user-profile-shared-resources",
    ),
    path(
        "profile/shared-resources",
        views.MegaRedProfileWithSharedResourcesView.as_view(),
        name="profile-shared-resources",
    ),
]
