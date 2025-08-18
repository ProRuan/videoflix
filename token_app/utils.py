import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    AccountActivationToken,
    AccountDeletionToken,
    PasswordResetToken,
)

User = get_user_model()


TOKEN_MAP = {
    "activation": AccountActivationToken,
    "deletion": AccountDeletionToken,
    "password_reset": PasswordResetToken,
}


def _generate_token_hex(nbytes: int = 20) -> str:
    """Return a hex token string (default 40 hex chars)."""
    return secrets.token_hex(nbytes)


def create_token_for_user(user: get_user_model, token_type: str):
    """
    Create or replace a token instance for user / token_type.
    Returns the token model instance.
    """
    Model = TOKEN_MAP[token_type]
    token_value = _generate_token_hex()
    # replace existing or create new
    obj, _ = Model.objects.update_or_create(
        user=user,
        defaults={"token": token_value, "created_at": timezone.now(),
                  "used": False},
    )
    return obj


def get_token_instance_by_value(token_value: str):
    """Find token instance across token models (returns instance or None)."""
    for Model in TOKEN_MAP.values():
        try:
            return Model.objects.get(token=token_value)
        except Model.DoesNotExist:
            continue
    return None


def token_expired(instance) -> bool:
    """Return True if the token instance is expired."""
    expires_at = instance.created_at + instance.lifetime
    return timezone.now() > expires_at


def token_expiry_datetime(instance):
    """Return the datetime when the token will expire."""
    return instance.created_at + instance.lifetime
