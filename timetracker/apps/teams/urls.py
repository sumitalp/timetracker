from django.urls import path

from timetracker.apps.teams.views import (
    TeamDashboardAPIView,
    TeamListCreateAPIView,
    TeamRetrieveUpdateAPIView,
    InvitationAcceptAPIView,
    TeamInviteAPIView,
)

urlpatterns = [
    path("", TeamListCreateAPIView.as_view(), name="team_list_create"),
    path(
        "<int:pk>/",
        TeamRetrieveUpdateAPIView.as_view(),
        name="team_update_retrieve",
    ),
    path(
        "<int:pk>/invite/",
        TeamInviteAPIView.as_view(),
        name="team_invite",
    ),
    path(
        "<int:pk>/invitation-accept/",
        InvitationAcceptAPIView.as_view(),
        name="accept_invitation",
    ),
    path(
        "<int:team_id>/dashboard/",
        TeamDashboardAPIView.as_view(),
        name="team_dashboard",
    ),
]