from celery.schedules import crontab
from celery.utils.log import get_task_logger
# from django.conf import settings
# from django.contrib.auth.forms import PasswordResetForm
from django.core.management import call_command

# from timetracker.apps.users.forms import PasswordSetConfirmation
# from timetracker.apps.users.utils import send_password_set_mail
from timetracker.celery import app

logger = get_task_logger(__name__)


@app.task
def flush_blacklisted_tokens():
    call_command("flushexpiredtokens")


@app.on_after_finalize.connect
def blacklisted_token_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week="sunday"), flush_blacklisted_tokens.s()
    )
