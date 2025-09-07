# Standard libraries
import re

# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user
from token_app.models import Token

HEX64 = re.compile(r"[0-9a-f]{64}")


@pytest.mark.django_db
def test_password_reset_success_sends_email_and_token():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:password-reset")
    res = APIClient().post(url, {"email": user.email}, format="json")

    assert res.status_code == 200
    assert res.data["email"] == user.email
    # token exists and is reset type
    qs = Token.objects.filter(user=user, type=Token.TYPE_RESET)
    assert qs.count() == 1
    # email content includes link with 64-hex token
    assert len(mail.outbox) == 1
    html = mail.outbox[0].alternatives[0][0]
    assert "http://localhost:4200/reset-password/" in html
    assert HEX64.search(html)


@pytest.mark.django_db
def test_password_reset_missing_email_returns_400():
    url = reverse("auth_app:password-reset")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 400
    assert "detail" in res.data


@pytest.mark.django_db
def test_password_reset_invalid_email_returns_400():
    url = reverse("auth_app:password-reset")
    res = APIClient().post(url, {"email": "invalid@@mail"}, format="json")
    assert res.status_code == 400
    assert "Enter a valid email address." in res.data["detail"]


@pytest.mark.django_db
def test_password_reset_user_not_found_returns_404():
    url = reverse("auth_app:password-reset")
    res = APIClient().post(url, {"email": "no.user@mail.com"}, format="json")
    assert res.status_code == 404
    assert "User not found" in res.data["detail"]
