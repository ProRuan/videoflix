# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user


@pytest.mark.django_db
def test_password_reset_success_existing_email():
    """Test for successful password reset with existing email."""
    user = make_user(email="john.doe@mail.com", is_active=True)
    url = reverse("auth_app:password_reset")
    res = APIClient().post(url, {"email": "john.doe@mail.com"}, format="json")
    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com"}
    assert len(mail.outbox) == 1
    assert "Reset your password" in mail.outbox[0].subject
    assert "reset-password" in mail.outbox[0].alternatives[0][0]
    assert AuthToken.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_password_reset_success_non_existing_email():
    """Test for successful password reset with non-existing email."""
    url = reverse("auth_app:password_reset")
    res = APIClient().post(url, {"email": "nobody@mail.com"}, format="json")
    assert res.status_code == 200
    assert res.json() == {"email": "nobody@mail.com"}
    assert len(mail.outbox) == 0
    assert AuthToken.objects.count() == 0


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": ""},
        {"email": "john"},
        {"email": "john.doe@mail"},
        {"email": "john.doe@mail.c"},
    ],
)
@pytest.mark.django_db
def test_password_reset_invalid_or_missing_email(payload):
    """Test for password reset with missing or invalid email."""
    url = reverse("auth_app:password_reset")
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == {
        "detail": ["Please check your email and try again."]
    }
