# Third-party suppliers
from django.utils import timezone
from knox.models import AuthToken


def delete_expired_knox_tokens() -> int:
    """Delete expired Knox tokens and return the deleted count."""
    now = timezone.now()
    qs = AuthToken.objects.filter(expiry__lt=now)
    count = qs.count()
    qs.delete()
    return count
