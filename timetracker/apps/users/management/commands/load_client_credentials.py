import json
import os

from django.conf import settings
from django.core.cache import cache
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = "LOAD Client Credentials of other known services"
    folder_name = settings.CLIENT_CREDENTIAL_FOLDER_NAME

    def folder_exists(self):
        return os.path.isdir(self.folder_name)

    def handle(self, *args, **options):
        if not self.folder_exists():
            raise CommandError(
                "{} folder doesn't exist. "
                "Perhaps the required volume has not been mounted".format(
                    self.folder_name
                )
            )

        for service_file_name in settings.OTHER_SERVICE_FILE_NAMES:
            with open(
                "{}/{}.txt".format(self.folder_name, service_file_name), "r"
            ) as f:
                data = json.loads(f.read())
                service_name = "{}-service".format(settings.SERVICE_FILE_NAME)
                cache.set(
                    service_name, data.get(service_name), timeout=None
                )  # Never expire. Default is 300 seconds
