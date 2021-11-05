from celery.utils.log import get_task_logger
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from timetracker.apps.teams.models import Team
from timetracker.apps.teams.configs import TeamStatus
from timetracker.apps.teams.utils import send_invitation

from timetracker.celery import app

logger = get_task_logger(__name__)


@app.task
def send_team_invitation(email, code, team_id):
    team = get_object_or_404(Team, pk=team_id, status=TeamStatus.ACTIVE)

    if team:
        send_invitation(email, code, team)
    else:
        logger.error("Team not found.")
