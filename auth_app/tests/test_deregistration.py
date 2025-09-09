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
    user = make_user(email="john.doe@mail.com",
                     password="Test123!", is_active=True)
    token = create_knox_token(user, hours=24)
    url = reverse("auth_app:deregistration")
    payload = {"token": token, "email": "john.doe@mail.com",
               "password": "Test123!"}

    res = APIClient().post(url, payload, format="json")

    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com"}
    # a new token for deletion email has been created
    assert AuthToken.objects.filter(user=user).count() == 2
    # email sent and link contains delete-account path
    assert len(mail.outbox) == 1
    assert "Confirm account deletion" in mail.outbox[0].subject
    assert "delete-account" in mail.outbox[0].alternatives[0][0]


@pytest.mark.parametrize(
    "payload",
    [
        {},  # all missing
        {"token": ""},  # blank token
        {"token": "bad token", "email": "john.doe@mail.com", "password": "x"},
        {"token": "A"*64, "email": "", "password": "Test123!"},
        {"token": "A"*64, "email": "john", "password": "Test123!"},
        {"token": "A"*64, "email": "john.doe@mail.com", "password": ""},  # blank pw
        # token valid but email doesn't match token's user
    ],
)
@pytest.mark.django_db
def test_deregistration_bad_requests(payload):
    user = make_user(email="john.doe@mail.com",
                     password="Test123!", is_active=True)
    create_knox_token(user, hours=24)
    url = reverse("auth_app:deregistration")

    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == BAD


@pytest.mark.django_db
def test_deregistration_email_mismatch_or_wrong_password():
    user = make_user(email="john.doe@mail.com",
                     password="Test123!", is_active=True)
    token = create_knox_token(user, hours=24)
    url = reverse("auth_app:deregistration")

    # email doesn't match the token's user
    res1 = APIClient().post(url, {
        "token": token, "email": "other@mail.com", "password": "Test123!"
    }, format="json")
    assert res1.status_code == 400
    assert res1.json() == BAD

    # wrong password
    res2 = APIClient().post(url, {
        "token": token, "email": "john.doe@mail.com", "password": "Wrong123!"
    }, format="json")
    assert res2.status_code == 400
    assert res2.json() == BAD


@pytest.mark.django_db
def test_deregistration_token_not_found():
    make_user(email="john.doe@mail.com", password="Test123!", is_active=True)
    url = reverse("auth_app:deregistration")
    payload = {"token": "A"*64,
               "email": "john.doe@mail.com", "password": "Test123!"}
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 404


@pytest.mark.django_db
def test_deregistration_expired_token_returns_400():
    user = make_user(email="john.doe@mail.com",
                     password="Test123!", is_active=True)
    token = create_knox_token(user, hours=-1)  # expired already
    url = reverse("auth_app:deregistration")
    payload = {"token": token, "email": "john.doe@mail.com",
               "password": "Test123!"}
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == BAD
