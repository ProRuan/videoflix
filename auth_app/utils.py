# Standard libraries
import re
from datetime import timedelta

# Third-party suppliers
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from knox.crypto import hash_token
from knox.models import AuthToken
from rest_framework.exceptions import ValidationError

# Local imports


EMAIL_RE = re.compile(
    r"^[A-ZÀ-Ÿa-zà-ÿß0-9._%+-]+@[A-ZÀ-Ÿa-zà-ÿß0-9.-]+\."
    r"[A-ZÀ-Ÿa-zà-ÿß]{2,}$"
)


def is_valid_email(email: str) -> bool:
    """Validate email against the provided unicode-aware pattern."""
    return bool(EMAIL_RE.match(email or ""))


def is_strong_password(pw: str) -> tuple[bool, str | None]:
    """Validate password against policy."""
    if re.search(r"[^A-Za-zÀ-Ÿà-ÿß0-9!@#$%^&*]", pw or ""):
        return False, "Not allowed special character."
    if len(pw or "") < 8:
        return False, "Use at least 8 characters."
    if not re.search(r"[A-ZÀ-Ÿ]", pw):
        return False, "Use at least one uppercase character."
    if not re.search(r"[a-zà-ÿß]", pw):
        return False, "Use at least one lowercase character."
    if not re.search(r"\d", pw):
        return False, "Use at least one digit."
    if not re.search(r"[!@#$%^&*]", pw):
        return False, "Use at least one special character."
    return True, None


def create_knox_token(user, hours: int) -> str:
    """Create a Knox token with a custom TTL (pass timedelta to manager)."""
    ttl = timedelta(hours=hours)
    obj, token = AuthToken.objects.create(user=user, expiry=ttl)
    return token


def build_activation_link(token: str) -> str:
    """Build activation link (frontend route)."""
    return f"http://localhost:4200/activate-account/{token}"


def send_activation_email(user, link: str) -> None:
    """Send activation email using the HTML template."""
    subject = "Activate your Videoflix account"
    html = render_to_string(
        "auth_app/account-activation-email.html",
        {"first_name": user.first_name, "link": link},
    )
    msg = EmailMultiAlternatives(subject, html, to=[user.email])
    msg.attach_alternative(html, "text/html")
    msg.send()


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


def build_reset_link(token: str) -> str:
    """Build password reset link (frontend route)."""
    return f"http://localhost:4200/reset-password/{token}"


def send_reset_email(email: str, link: str) -> None:
    """Send password reset email using the provided HTML template."""
    subject = "Reset your password"
    html = render_to_string(
        "auth_app/password-reset-email.html", {"link": link})
    msg = EmailMultiAlternatives(subject, html, to=[email])
    msg.attach_alternative(html, "text/html")
    msg.send()


def build_deletion_link(token: str) -> str:
    """Build account deletion link (frontend route)."""
    return f"http://localhost:4200/delete-account/{token}"


def send_deletion_email(user, link: str) -> None:
    """Send deletion confirmation email using the HTML template."""
    html = render_to_string(
        "auth_app/account-deletion-email.html",
        {"first_name": user.first_name, "link": link},
    )
    msg = EmailMultiAlternatives(
        "Confirm account deletion", html, to=[user.email])
    msg.attach_alternative(html, "text/html")
    msg.send()
