# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token

BAD = {"detail": ["Please check your input and try again."]}


def _url():
    """Get URL."""
    return reverse("auth_app:password_update")


def _auth_client(token: str) -> APIClient:
    """Get auth client."""
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    return c


def _login(email: str, password: str):
    """Log in user."""
    return APIClient().post(
        reverse("auth_app:login"),
        {"email": email, "password": password},
        format="json",
    )


@pytest.mark.django_db
def test_password_update_success():
    """Test for successful password update."""
    user = make_user(email="john.doe@mail.com", password="OldPass1!",
                     is_active=True)
    token = create_knox_token(user, hours=1)
    payload = {"email": user.email, "password": "NewPass1!",
               "repeated_password": "NewPass1!"}
    res = _auth_client(token).post(_url(), payload, format="json")
    assert res.status_code == 200 and res.json() == {
        "email": user.email, "user_id": user.id
    }
    assert AuthToken.objects.count() == 0
    assert _login(user.email, "NewPass1!").status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": ""},
        {"email": "john"},
        {"email": "john.doe@mail.com"},
        {"email": "john.doe@mail.com", "password": ""},
        {"email": "john.doe@mail.com", "password": "short",
         "repeated_password": "short"},
        {"email": "john.doe@mail.com", "password": "test123!",
         "repeated_password": "test123!"},
        {"email": "john.doe@mail.com", "password": "TEST123!",
         "repeated_password": "TEST123!"},
        {"email": "john.doe@mail.com", "password": "Testabc!",
         "repeated_password": "Testabc!"},
        {"email": "john.doe@mail.com", "password": "Test1234",
         "repeated_password": "Test1234"},
        {"email": "john.doe@mail.com", "password": "NewPass1!",
         "repeated_password": "Other1!"},
        {"email": "other@mail.com", "password": "NewPass1!",
         "repeated_password": "NewPass1!"},
    ],
)
@pytest.mark.django_db
def test_password_update_bad_request(payload):
    """Test for password update with invalid data."""
    user = make_user(email="john.doe@mail.com", password="OldPass1!",
                     is_active=True)
    token = create_knox_token(user, hours=1)
    res = _auth_client(token).post(_url(), payload, format="json")
    assert res.status_code == 400 and res.json() == BAD


@pytest.mark.django_db
def test_password_update_unauthorized():
    """Test for password update with unauthorized user."""
    res = APIClient().post(_url(), {}, format="json")
    assert res.status_code == 401
