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


@pytest.mark.django_db
def test_deregistration_success():
    """Test for successful deregistration."""
    user = make_user(email="john.doe@mail.com", password="Test123!",
                     is_active=True)
    token = create_knox_token(user, hours=24)
    url = reverse("auth_app:deregistration")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, {
        "email": "john.doe@mail.com", "password": "Test123!"
    }, format="json")
    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com"}
    assert AuthToken.objects.filter(user=user).count() == 2
    assert len(mail.outbox) == 1
    assert "Confirm account deletion" in mail.outbox[0].subject
    assert "delete-account" in mail.outbox[0].alternatives[0][0]


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
    """Test for deregistration with missing or invalid data."""
    user = make_user(email="john.doe@mail.com", password="Test123!",
                     is_active=True)
    token = create_knox_token(user, hours=24)
    url = reverse("auth_app:deregistration")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == BAD


@pytest.mark.django_db
def test_deregistration_unauthorized():
    """Test for deregistration with unauthorized user."""
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {"email": "john.doe@mail.com",
                                 "password": "Test123!"}, format="json")
    assert res.status_code == 401
