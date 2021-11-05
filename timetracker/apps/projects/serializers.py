from django.db import IntegrityError
from rest_framework import serializers

from timetracker.apps.projects.models import Entry, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = (
            "created_by",
        )

    
    def create(self, validated_data):
        request = self.context.get("request")
        title = validated_data.get("title")
        team = validated_data.get("team")
        try:
            project = Project.objects.create(
                title=title,
                team=team,
                created_by=request.user,
            )
            
            return project
        except IntegrityError as integrity_error:
            raise serializers.ValidationError({
                "detail": f"Some error has occurred while creating project: {integrity_error}"
            })


    def update(self, instance, validated_data):
        request = self.context.get("request")
        if(instance.created_by != request.user):
            raise serializers.ValidationError({
                "detail": f"You are not authorize to update this project."
            })
        return super().update(instance, validated_data)  


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = "__all__"  
        read_only_fields = (
            "created_by",
            "minutes",
            "is_tracked"
        )


    def create(self, validated_data):
        request = self.context.get("request")
        started_at = validated_data.get("started_at")
        ended_at = validated_data.get("ended_at")
        if not started_at:
            raise serializers.ValidationError(
                {
                    "started_at": "This field is required."
                }
            )

        if not ended_at:
            raise serializers.ValidationError(
                {
                    "ended_at": "This field is required."
                }
            )
        try:
            data = {
                **validated_data
            }
            data['created_by'] = request.user
            difference = ended_at - started_at
            minutes, seconds = divmod(difference.days * (24*3600) + difference.seconds, 60)
            data['minutes'] = minutes + (seconds/100)
            data['is_tracked'] = True
            
            entry = Entry.objects.create(
                **data
            )
            
            return entry
        except IntegrityError as integrity_error:
            raise serializers.ValidationError({
                "detail": f"Some error has occurred while creating entry: {integrity_error}"
            })

    
    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        ended_at = validated_data.get('ended_at', instance.ended_at)
        started_at = validated_data.get('started_at', instance.started_at)

        difference = ended_at - started_at
        minutes, seconds = divmod(diffrence.days * (24*3600) + difference.seconds, 60)
        instance.minutes = minutes + (seconds/100)

        instance.save()
        return instance
