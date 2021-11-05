from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenBackendError, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .managers import CustomUserManager
from timetracker.apps.projects.models import Project
from timetracker.apps.teams.configs import TeamStatus


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = None
    email = models.EmailField(_("email address"), unique=True, max_length=50)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def blacklist_outstanding_tokens(self):
        tokens = self.outstandingtoken_set.values_list("token", flat=True)

        for token in tokens:
            try:
                token = RefreshToken(token)
            except (TokenBackendError, TokenError):
                pass
            else:
                token.blacklist()

    def my_teams(self):
        return self.teams.all(status=TeamStatus.ACTIVE)


    def my_own_projects(self):
        return self.projects.all()

    
    def my_all_projects(self):
        all_teams = self.my_teams()
        own_projects = self.my_own_projects()
        others_projects = Project.objects.filter(
            team__in=all_teams.filter(
                ~Q(created_by=self)
            )
        )

        if own_projects or others_projects:
            return (
                own_projects.union(others_projects)
                if own_projects
                else others_projects.union(own_projects)
            )
        return QuerySet(model=Project)
