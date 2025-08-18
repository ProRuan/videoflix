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
    Remove any existing token for this user & token_type and create a fresh one.
    Returns the new token model instance.
    """
    Model = TOKEN_MAP[token_type]
    # remove existing token for that user (OneToOne semantics)
    Model.objects.filter(user=user).delete()
    token_value = _generate_token_hex()
    instance = Model.objects.create(token=token_value, user=user)
    return instance


def get_token_and_type_by_value(token_value: str):
    """
    Find token instance across token models.
    Returns (instance, type_str) or (None, None).
    """
    for type_str, Model in TOKEN_MAP.items():
        inst = Model.objects.filter(token=token_value).first()
        if inst:
            return inst, type_str
    return None, None


def token_expired(instance) -> bool:
    """Return True if the token instance is expired."""
    expires_at = instance.created_at + instance.lifetime
    return timezone.now() > expires_at


def token_expiry_datetime(instance):
    """Return the datetime when the token will expire."""
    return instance.created_at + instance.lifetime
