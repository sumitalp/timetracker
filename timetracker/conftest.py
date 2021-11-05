# fixtures to be accessed globally across all tests can be put here
import pytest
from rest_framework.test import APIClient

from timetracker.apps.crawlers.tests.factories import YTChannelFactory, YTVideoFactory


@pytest.fixture(autouse=True)
def enable_db_access(db):
    """
    Global DB access to all tests.
    :param db:
    :return:
    """
    pass


@pytest.fixture
def synchronize_celery_tasks(settings):
    """
    https://pytest-django.readthedocs.io/en/latest/helpers.html#settings
    :param settings:
    :return:
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True


@pytest.fixture
def client():
    """
    better off using rest framework's api client instead of built in django test client for pytest
    since we'll be working with developing and testing apis
    :return:
    """
    return APIClient()


@pytest.fixture
def channel():
    return YTChannelFactory()


@pytest.fixture
def video():
    return YTVideoFactory()
