# Standard libraries

# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user


@pytest.mark.django_db
def test_registration_success():
    url = reverse("auth_app:registration")
    payload = {"email": "john.doe@mail.com",
               "password": "Test123!",
               "repeated_password": "Test123!"}
    res = APIClient().post(url, data=payload, format="json")

    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "john.doe@mail.com"
    assert body["is_active"] is False
    assert body["user_id"] > 0

    assert len(mail.outbox) == 1
    assert "Activate your account" in mail.outbox[0].subject
    assert "activate-account" in mail.outbox[0].alternatives[0][0]
    assert AuthToken.objects.count() == 1


@pytest.mark.parametrize("good", ["john.doe@mail.com", "j@m.eu"])
@pytest.mark.django_db
def test_registration_email_good(good):
    url = reverse("auth_app:registration")
    data = {"email": good, "password": "Test123!",
            "repeated_password": "Test123!"}
    res = APIClient().post(url, data=data, format="json")
    assert res.status_code == 201


@pytest.mark.parametrize(
    "email,err",
    [
        ("", {"email": ["This field may not be blank."]}),
        ("john", {"email": ["Enter a valid email address."]}),
        ("john.doe@mail", {"email": ["Enter a valid email address."]}),
        ("john.doe@mail.c", {"email": ["Enter a valid email address."]}),
    ],
)
@pytest.mark.django_db
def test_registration_email_bad(email, err):
    url = reverse("auth_app:registration")
    data = {"email": email, "password": "Test123!",
            "repeated_password": "Test123!"}
    res = APIClient().post(url, data=data, format="json")
    assert res.status_code == 400
    assert res.json() == err


@pytest.mark.django_db
def test_registration_email_exists():
    make_user(email="john.doe@mail.com")
    url = reverse("auth_app:registration")
    data = {"email": "john.doe@mail.com", "password": "Test123!",
            "repeated_password": "Test123!"}
    res = APIClient().post(url, data=data, format="json")
    assert res.status_code == 400
    assert res.json() == {"email": ["Email already exists."]}


@pytest.mark.parametrize(
    "pw,err",
    [
        ("", {"password": ["This field may not be blank."]}),
        ("Testabc+", {"password": ["Not allowed special character."]}),
        ("Test", {"password": ["Use at least 8 characters."]}),
        ("test123!", {"password": ["Use at least one uppercase character."]}),
        ("TEST123!", {"password": ["Use at least one lowercase character."]}),
        ("Testabc!", {"password": ["Use at least one digit."]}),
        ("Test1234", {"password": ["Use at least one special character."]}),
    ],
)
@pytest.mark.django_db
def test_registration_password_bad(pw, err):
    url = reverse("auth_app:registration")
    data = {"email": "john.doe@mail.com", "password": pw,
            "repeated_password": pw}
    res = APIClient().post(url, data=data, format="json")
    assert res.status_code == 400
    assert res.json() == err
