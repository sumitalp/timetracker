import json
import os

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from oauth2_provider.models import get_application_model

from timetracker.utils import encode_client_credentials


class Command(BaseCommand):
    help = "Create Client Credentials for known services"
    folder_name = settings.CLIENT_CREDENTIAL_FOLDER_NAME

    def folder_exists(self):
        return os.path.isdir(self.folder_name)

    def handle(self, *args, **options):
        for key, value in settings.SERVICE_NAMES.items():
            file_name = settings.SERVICE_FILE_NAME
            Application = get_application_model()
            application, created = Application.objects.get_or_create(
                name=value,
                defaults={
                    "client_type": Application.CLIENT_CONFIDENTIAL,
                    "authorization_grant_type": Application.GRANT_CLIENT_CREDENTIALS,
                },
            )
            print(settings.HOME_DIR)
            auth_string = encode_client_credentials(
                application.client_id, application.client_secret
            )

            if not self.folder_exists():
                raise CommandError(
                    "{} folder doesn't exist. "
                    "Perhaps the required volume has not been mounted".format(
                        self.folder_name
                    )
                )

            with open("{}/{}.txt".format(self.folder_name, file_name), mode="w+") as f:
                data = json.dumps({value: auth_string.decode("utf-8")})
                f.write(data)
