from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from timetracker.apps.users.tasks import flush_blacklisted_tokens


class TestTokenFlush:
    def test_token_entry_flush(self, synchronize_celery_tasks, user):
        refresh_token = RefreshToken().for_user(user)
        refresh_token.blacklist()
        OutstandingToken.objects.filter(
            user_id=user.id, token__exact=str(refresh_token)
        ).update(expires_at=timezone.now())
        assert OutstandingToken.objects.count() == 1
        assert BlacklistedToken.objects.count() == 1
        flush_blacklisted_tokens.delay()
        assert not OutstandingToken.objects.count()
        assert not BlacklistedToken.objects.count()
