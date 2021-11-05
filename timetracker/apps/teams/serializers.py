from django.db import IntegrityError
from rest_framework import serializers

from timetracker.apps.teams.models import Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"
        read_only_fields = (
            "created_by", "members"
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["status"] = instance.get_status_display()

        return data

    
    def create(self, validated_data):
        request = self.context.get("request")
        title = validated_data.get("title")

        try:
            team = Team.objects.create(
                title=title,
                created_by=request.user,
            )
            team.members.add(request.user)
            team.save()
            
            return team
        except IntegrityError as integrity_error:
            raise serializers.ValidationError(
                f"Some error has occurred while creating team: {integrity_error}"
            )


class TeamInvitationSerializer(serializers.Serializer):
    team = serializers.IntegerField()
    email = serializers.EmailField()


class AcceptInvitationSerializer(serializers.Serializer):
    code = serializers.CharField()
