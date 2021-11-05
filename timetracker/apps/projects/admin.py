from django.contrib import admin
from timetracker.apps.projects.models import Entry, Project

# Register your models here.
admin.site.register(Project)
admin.site.register(Entry)
