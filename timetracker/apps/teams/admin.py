from django.contrib import admin
from timetracker.apps.teams.models import Invitation, Team

# Register your models here.
admin.site.register(Team)
admin.site.register(Invitation)
