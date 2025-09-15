# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user


BAD = {"detail": ["Please check your login data and try again."]}


@pytest.mark.django_db
def test_login_success():
    """Test for successful login."""
    user = make_user(email="john.doe@mail.com", password="Test123!",
                     is_active=True)
    url = reverse("auth_app:login")
    payload = {"email": "john.doe@mail.com", "password": "Test123!"}
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "john.doe@mail.com"
    assert body["user_id"] == user.id
    assert isinstance(body.get("token"), str) and len(body["token"]) > 10
    assert AuthToken.objects.filter(user=user).count() == 1


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": ""},
        {"email": "john"},
        {"email": "john.doe@mail.com"},
        {"email": "john.doe@mail.com", "password": ""},
        {"email": "nouser@mail.com", "password": "Test123!"},
        {"email": "john.doe@mail.com", "password": "Wrong123!"},
    ],
)
@pytest.mark.django_db
def test_login_failed_authentication(payload):
    """Test for login with failed authentication."""
    make_user(email="john.doe@mail.com", password="Test123!", is_active=True)
    url = reverse("auth_app:login")
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == BAD
