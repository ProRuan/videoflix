# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token

BAD = {"detail": ["Please check your input and try again."]}


def _url():
    """Get URL."""
    return reverse("auth_app:deregistration")


def _auth_client(token: str) -> APIClient:
    """Get auth client."""
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    return c


def _payload(email="john.doe@mail.com", pw="Test123!"):
    """Get deregistration payload."""
    return {"email": email, "password": pw}


@pytest.mark.django_db
def test_deregistration_success():
    """Test for successful deregistration."""
    user = make_user(email="john.doe@mail.com", password="Test123!",
                     is_active=True)
    token = create_knox_token(user, hours=24)
    res = _auth_client(token).post(_url(), _payload(), format="json")
    assert res.status_code == 200 and res.json() == {"email": user.email}
    assert AuthToken.objects.filter(user=user).count() == 2
    assert len(mail.outbox) == 1
    msg = mail.outbox[0]
    assert "Confirm account deletion" in msg.subject
    assert "delete-account" in msg.alternatives[0][0]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": ""},
        {"email": "john"},
        {"email": "john.doe@mail.com"},
        {"email": "other@mail.com", "password": "Test123!"},
        {"email": "john.doe@mail.com", "password": "Wrong123!"},
    ],
)
@pytest.mark.django_db
def test_deregistration_bad_requests(payload):
    """Test for deregistration with invalid data."""
    user = make_user(email="john.doe@mail.com", password="Test123!",
                     is_active=True)
    token = create_knox_token(user, hours=24)
    res = _auth_client(token).post(_url(), payload, format="json")
    assert res.status_code == 400 and res.json() == BAD


@pytest.mark.django_db
def test_deregistration_unauthorized():
    """Test for deregistration with unauthorized user."""
    res = APIClient().post(_url(), _payload(), format="json")
    assert res.status_code == 401
