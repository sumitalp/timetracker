from django.db import models
from timetracker.apps.teams.models import Team


class Project(models.Model):
    team = models.ForeignKey(Team, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        "users.User", related_name="projects", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def registered_time(self):
        return sum(float(entry.minutes) for entry in self.entries.all())



class Entry(models.Model):
    project = models.ForeignKey(
        Project, related_name="entries", on_delete=models.CASCADE, blank=True, null=True
    )
    minutes = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    is_tracked = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "users.User", related_name="entries", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.project:
            return f"{self.project.title} - {self.created_at}"

        return f"{self.created_at}"
