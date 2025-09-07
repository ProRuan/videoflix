# Standard libraries
import re
from typing import Optional

# Third-party suppliers
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

# Local imports


EMAIL_RE = re.compile(
    r"^[A-ZÀ-Ÿa-zà-ÿß0-9._%+-]+@[A-ZÀ-Ÿa-zà-ÿß0-9.-]+\.[A-ZÀ-Ÿa-ÿß]{2,}$"
)
PWD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
    r"(?=.*[^\w\s]).{8,}$"
)


def is_valid_email(email: str) -> bool:
    """Return True if email matches the project pattern."""
    return bool(EMAIL_RE.match(email or ""))


def is_strong_password(password: str) -> bool:
    """Return True if password meets strength requirements."""
    return bool(PWD_RE.match(password or ""))


def build_activation_link(token_value: Optional[str]) -> str:
    token = token_value or ""
    return f"http://localhost:4200/activate-account/{token}"


def send_activation_email(email: str, first_name: str, token: Optional[str]) -> None:
    """Render and send the activation email (HTML + plaintext)."""
    ctx = {"first_name": first_name or "",
           "link": build_activation_link(token)}
    html = render_to_string("auth_app/account-activation-email.html", ctx)
    msg = EmailMultiAlternatives(
        subject="Confirm your email • Videoflix",
        body="Please open this email in an HTML-capable client.",
        to=[email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


def build_password_reset_link(token_value: Optional[str]) -> str:
    token = token_value or ""
    return f"http://localhost:4200/reset-password/{token}"


def send_password_reset_email(email: str, first_name: str,
                              token: Optional[str]) -> None:
    ctx = {"first_name": first_name or "",
           "link": build_password_reset_link(token)}
    html = render_to_string("auth_app/password-reset-email.html", ctx)
    msg = EmailMultiAlternatives(
        subject="Reset your password • Videoflix",
        body="Please open this email in an HTML-capable client.",
        to=[email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


def build_account_deletion_link(token_value: Optional[str]) -> str:
    """Build frontend deletion URL including the raw token."""
    token = token_value or ""
    return f"http://localhost:4200/delete-account/{token}"


def send_account_deletion_email(email: str, first_name: str,
                                token: Optional[str]) -> None:
    """Render and send the account deletion email (HTML)."""
    ctx = {"first_name": first_name or "",
           "link": build_account_deletion_link(token)}
    html = render_to_string("auth_app/account-deletion-email.html", ctx)
    msg = EmailMultiAlternatives(
        subject="Confirm account deletion • Videoflix",
        body="Please open this email in an HTML-capable client.",
        to=[email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()
