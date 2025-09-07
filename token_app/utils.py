# Standard libraries
import re
from datetime import timedelta
from typing import Optional, Tuple

# Third-party suppliers
from django.utils import timezone
from django.contrib.auth import get_user_model

# Local imports
from token_app.models import Token


HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def token_lifetime_delta(token_type: str) -> timedelta:
    """Return lifetime delta based on token type."""
    if token_type == Token.TYPE_AUTH:
        return timedelta(hours=12)
    if token_type in (Token.TYPE_ACTIVATION, Token.TYPE_DELETION):
        return timedelta(hours=24)
    if token_type == Token.TYPE_RESET:
        return timedelta(hours=1)
    return timedelta(hours=1)


def generate_token_value() -> str:
    """Create a 64-char hex string (Knox-compatible length)."""
    from secrets import token_hex
    return token_hex(32)


def upsert_token(user_id: int, token_type: str) -> Token:
    """Delete active same-type tokens, then create a fresh one."""
    now = timezone.now()
    Token.objects.filter(user_id=user_id, type=token_type, used=False,
                         expired_at__gt=now).delete()
    value = generate_token_value()
    exp = now + token_lifetime_delta(token_type)
    return Token.objects.create(user_id=user_id, type=token_type,
                                value=value, expired_at=exp)


def fetch_token(value: str) -> Optional[Token]:
    """Return token by value or None."""
    try:
        return Token.objects.select_related("user").get(value=value)
    except Token.DoesNotExist:
        return None


def classify_token_status(tok: Optional[Token]) -> Tuple[str, Optional[str]]:
    """Classify token status and return (status, message)."""
    if tok is None:
        return "not_found", "Token not found."
    if not HEX64_RE.match(tok.value):
        return "invalid", "Invalid token pattern."
    if tok.used:
        return "used", "Token already used."
    if tok.expired_at <= timezone.now():
        return "expired", "Token expired."
    return "valid", None


def mark_token_used(tok: Token) -> None:
    """Mark token as used."""
    tok.used = True
    tok.save(update_fields=["used"])
