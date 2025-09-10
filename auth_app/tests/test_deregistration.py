# Standard libraries

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
    # a new token for deletion email has been created and email sent
    assert AuthToken.objects.filter(user=user).count() == 2
    assert len(mail.outbox) == 1
    assert "Confirm account deletion" in mail.outbox[0].subject
    assert "delete-account" in mail.outbox[0].alternatives[0][0]


@pytest.mark.parametrize(
    "payload",
    [
        {},  # missing all
        {"email": ""},  # blank email
        {"email": "john"},  # invalid email
        {"email": "john.doe@mail.com"},  # missing password
        {"email": "other@mail.com", "password": "Test123!"},  # mismatch email
        {"email": "john.doe@mail.com", "password": "Wrong123!"},  # bad pw
    ],
)
@pytest.mark.django_db
def test_deregistration_bad_requests(payload):
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
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {"email": "john.doe@mail.com",
                                 "password": "Test123!"}, format="json")
    assert res.status_code == 401
