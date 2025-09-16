# Standard libraries
import re
from datetime import timedelta

# Third-party suppliers
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from knox.crypto import hash_token
from knox.models import AuthToken
from rest_framework import serializers

EMAIL_RE = re.compile(
    r"^[A-ZÀ-Ÿa-zà-ÿß0-9._%+-]+@[A-ZÀ-Ÿa-zà-ÿß0-9.-]+\.[A-ZÀ-Ÿa-zà-ÿß]{2,}$"
)
FORBIDDEN_EMAIL_RE = re.compile(r"[^A-ZÀ-Ÿa-ÿß0-9._%+\-@]")

PW_MIN_LENGTH = 8
FORBIDDEN_PW_RE = re.compile(r"[^A-Za-zÀ-Ÿà-ÿß0-9!@#$%^&*]")
UPPER_RE = re.compile(r"[A-ZÀ-Ÿ]")
LOWER_RE = re.compile(r"[a-zà-ÿß]")
DIGIT_RE = re.compile(r"\d")
SPECIAL_RE = re.compile(r"[!@#$%^&*]")

ACTIVATION_TTL_H = 24
REACTIVATION_TTL_H = 24
LOGIN_TTL_H = 12
RESET_TTL_H = 1
DELETION_TTL_H = 24


def get_frontend_url() -> str:
    """Get base frontend URL with localhost fallback."""
    base = getattr(settings, "FRONTEND_URL", "http://localhost:4200")
    return base.rstrip("/")


def build_frontend_link(path: str) -> str:
    """Build absolute link for frontend routes."""
    return f"{get_frontend_url()}/{path.lstrip('/')}"


def is_valid_email(email: str) -> bool:
    """Check email against the unicode-aware pattern."""
    return bool(EMAIL_RE.match(email or ""))


def has_email_forbidden_char(email: str) -> bool:
    """Check email for not allowed characters."""
    return bool(FORBIDDEN_EMAIL_RE.search(email or ""))


def validate_email_or_raise(email: str) -> None:
    """Validate email and raise DRF ValidationError on failures."""
    if email == "":
        raise serializers.ValidationError("This field may not be blank.")
    if has_email_forbidden_char(email):
        raise serializers.ValidationError("Not allowed special character.")
    if not is_valid_email(email):
        raise serializers.ValidationError("Enter a valid email address.")


def validate_email_unique(email: str) -> None:
    """Ensure email is unique for the user model."""
    user_model = get_user_model()
    if user_model.objects.filter(email__iexact=email).exists():
        raise serializers.ValidationError("Email already exists.")


def is_strong_password(password: str) -> tuple[bool, str | None]:
    """Check password policy and return (ok, message)."""
    if FORBIDDEN_PW_RE.search(password or ""):
        return False, "Not allowed special character."
    if len(password or "") < PW_MIN_LENGTH:
        return False, "Use at least 8 characters."
    if not UPPER_RE.search(password or ""):
        return False, "Use at least one uppercase character."
    if not LOWER_RE.search(password or ""):
        return False, "Use at least one lowercase character."
    if not DIGIT_RE.search(password or ""):
        return False, "Use at least one digit."
    if not SPECIAL_RE.search(password or ""):
        return False, "Use at least one special character."
    return True, None


def validate_passwords(password: str, confirm: str | None = None) -> None:
    """Validate password and optional confirmation."""
    if password == "":
        raise serializers.ValidationError(
            {"password": ["This field may not be blank."]}
        )
    ok, msg = is_strong_password(password)
    if not ok:
        raise serializers.ValidationError({"password": [msg]})
    if confirm is not None and password != confirm:
        raise serializers.ValidationError(
            {"password": ["Passwords must match."]}
        )


def create_knox_token(user, hours: int) -> str:
    """Create a Knox token with a custom lifetime in hours."""
    ttl = timedelta(hours=hours)
    _, token = AuthToken.objects.create(user=user, expiry=ttl)
    return token


def resolve_knox_token(raw: str):
    """Return AuthToken for raw token or None; delete if expired."""
    if not raw:
        return None
    digest = hash_token(raw)
    try:
        token = AuthToken.objects.select_related("user").get(digest=digest)
    except AuthToken.DoesNotExist:
        return None
    if token.expiry and timezone.now() > token.expiry:
        token.delete()
        raise serializers.ValidationError("Token expired.")
    return token


def build_activation_link(token: str) -> str:
    """Build link for account activation."""
    return build_frontend_link(f"activate-account/{token}")


def build_reset_link(token: str) -> str:
    """Build link for password reset."""
    return build_frontend_link(f"reset-password/{token}")


def build_deletion_link(token: str) -> str:
    """Build link for account deletion."""
    return build_frontend_link(f"delete-account/{token}")


def _send_html_email(subject: str, html: str, to_email: str) -> None:
    """Send a single-recipient HTML email."""
    msg = EmailMultiAlternatives(subject, html, to=[to_email])
    msg.attach_alternative(html, "text/html")
    msg.send()


def send_activation_email(user, link: str) -> None:
    """Send account activation email."""
    html = render_to_string(
        "auth_app/account-activation-email.html",
        {"first_name": getattr(user, "first_name", ""), "link": link},
    )
    _send_html_email("Activate your account", html, user.email)


def send_reset_email(email: str, link: str) -> None:
    """Send password reset email."""
    html = render_to_string(
        "auth_app/password-reset-email.html", {"link": link})
    _send_html_email("Reset your password", html, email)


def send_deletion_email(user, link: str) -> None:
    """Send account deletion confirmation email."""
    html = render_to_string(
        "auth_app/account-deletion-email.html",
        {"first_name": getattr(user, "first_name", ""), "link": link},
    )
    _send_html_email("Confirm account deletion", html, user.email)


def reauthenticate(request, email: str, password: str):
    """Return the user if credentials are valid, else None."""
    return authenticate(request, email=email, password=password)
