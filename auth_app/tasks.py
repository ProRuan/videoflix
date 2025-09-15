# Third-party suppliers
from django.utils import timezone
from knox.models import AuthToken


def delete_user_expired_knox_tokens(user_id: int) -> int:
    """Delete expired Knox tokens for a user and return deleted count."""
    now = timezone.now()
    qs = AuthToken.objects.filter(user_id=user_id, expiry__lt=now)
    count = qs.count()
    qs.delete()
    return count
