import random

from rest_framework import status
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from timetracker.apps.teams.configs import InviteStatus
from timetracker.apps.teams.models import Invitation, Team
from timetracker.apps.teams.serializers import AcceptInvitationSerializer, TeamInvitationSerializer, TeamSerializer
from timetracker.apps.teams.tasks import send_team_invitation


class TeamListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.all()


class TeamRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.all()


class TeamInviteAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TeamInvitationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = get_object_or_404(Team, pk=serializer.data.get('team'), status=Team.ACTIVE)
        email = serializer.data.get('email')

        if email:
            invitations = Invitation.objects.filter(team=team, email=email)

            if not invitations.exists():
                code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz123456789') for i in range(4))
                invitation = Invitation.objects.create(team=team, email=email, code=code)

                send_team_invitation.delay(email, code, team.id)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class InvitationAcceptAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AcceptInvitationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.data.get('code')

        invitations = Invitation.objects.filter(code=code, email=request.user.email, status=InviteStatus.INVITED)

        if invitations.exists():
            invitation = invitations[0]
            invitation.status = InviteStatus.ACCEPTED
            invitation.save()

            team = invitation.team
            team.members.add(request.user)
            team.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

