# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user


def _url():
    """Get URL."""
    return reverse("auth_app:registration")


def _post(email: str, pw: str):
    """Post registration data."""
    data = {"email": email, "password": pw, "repeated_password": pw}
    return APIClient().post(_url(), data=data, format="json")


@pytest.mark.django_db
def test_registration_success():
    """Test for successful registration."""
    res = _post("john.doe@mail.com", "Test123!")
    body = res.json()
    assert res.status_code == 201
    assert body["email"] == "john.doe@mail.com"
    assert body["is_active"] is False and body["user_id"] > 0
    assert len(mail.outbox) == 1
    assert "Activate your account" in mail.outbox[0].subject
    assert "activate-account" in mail.outbox[0].alternatives[0][0]
    assert AuthToken.objects.count() == 1


@pytest.mark.parametrize("good", ["john.doe@mail.com", "j@m.eu"])
@pytest.mark.django_db
def test_registration_email_good(good):
    """Test for successful registration with good email."""
    assert _post(good, "Test123!").status_code == 201


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
    """Test for registration with bad email."""
    res = _post(email, "Test123!")
    assert res.status_code == 400 and res.json() == err


@pytest.mark.parametrize(
    "forbidden",
    [
        "john!doe@mail.com",
        "john.d#e@mail.com",
    ],
)
@pytest.mark.django_db
def test_registration_email_forbidden_chars(forbidden):
    """Test for registration with forbidden email."""
    res = _post(forbidden, "Test123!")
    assert res.status_code == 400
    assert res.json() == {"email": ["Not allowed special character."]}


@pytest.mark.django_db
def test_registration_email_exists():
    """Test for registration with already existing email."""
    make_user(email="john.doe@mail.com")
    res = _post("john.doe@mail.com", "Test123!")
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
    """Test for registration with bad password."""
    res = _post("john.doe@mail.com", pw)
    assert res.status_code == 400 and res.json() == err
