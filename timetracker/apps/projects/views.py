from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from timetracker.apps.projects.models import Entry, Project
from timetracker.apps.projects.serializers import EntrySerializer, ProjectSerializer


class ProjectListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()


class ProjectRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()


class EntryListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EntrySerializer

    def get_queryset(self):
        return Entry.objects.all()


class EntryRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EntrySerializer

    def get_queryset(self):
        return Entry.objects.all()
