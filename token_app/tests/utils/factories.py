# Standard libraries
from datetime import timedelta

# Third-party suppliers
from django.contrib.auth import get_user_model
from django.utils import timezone

# Local imports
from token_app.models import Token
from token_app.utils import generate_token_value


def make_user(email: str):
    """Create a user with default password."""
    User = get_user_model()
    return User.objects.create_user(email=email, password="Test123!")


def make_token(user, ttype: str, hours_delta: int = 1, used: bool = False):
    """Create a token with flexible expiry and usage."""
    value = generate_token_value()
    exp = timezone.now() + timedelta(hours=hours_delta)
    return Token.objects.create(user=user, type=ttype, value=value,
                                expired_at=exp, used=used)
