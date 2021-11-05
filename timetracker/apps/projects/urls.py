from django.urls import path

from timetracker.apps.projects.views import (
    EntryListCreateAPIView,
    EntryRetrieveUpdateAPIView,
    ProjectListCreateAPIView,
    ProjectRetrieveUpdateAPIView
)

urlpatterns = [
    path("", ProjectListCreateAPIView.as_view(), name="project_list_create"),
    path(
        "<int:pk>/",
        ProjectRetrieveUpdateAPIView.as_view(),
        name="project_update_retrieve",
    ),
    path("<int:project_id>/entries/", EntryListCreateAPIView.as_view(), name="entry_list_create"),
    path(
        "<int:project_id>/entries/<int:pk>/",
        EntryRetrieveUpdateAPIView.as_view(),
        name="entry_update_retrieve",
    ),
]