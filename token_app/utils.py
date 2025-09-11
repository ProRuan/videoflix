# Standard libraries

# Third-party suppliers
from django.utils import timezone
from knox.crypto import hash_token
from knox.models import AuthToken
from rest_framework.exceptions import ValidationError

# Local imports


def resolve_knox_token(raw: str):
    """Return AuthToken for raw token; raise on expired; None if missing."""
    digest = hash_token(raw)
    try:
        obj = AuthToken.objects.select_related("user").get(digest=digest)
    except AuthToken.DoesNotExist:
        return None
    if obj.expiry and timezone.now() > obj.expiry:
        obj.delete()
        raise ValidationError("Token expired.")
    return obj
