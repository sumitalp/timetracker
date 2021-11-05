from django.db import models

from timetracker.apps.teams.configs import InviteStatus, TeamStatus



class Team(models.Model):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField("users.User", related_name="teams")
    created_by = models.ForeignKey(
        "users.User", related_name="created_teams", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=TeamStatus.CHOICES, default=TeamStatus.ACTIVE
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Invitation(models.Model):
    team = models.ForeignKey(Team, related_name="invitations", on_delete=models.CASCADE)
    email = models.EmailField()
    code = models.CharField(max_length=20)
    status = models.IntegerField(choices=InviteStatus.CHOICES, default=InviteStatus.INVITED)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
