# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token

BAD = {"detail": ["Please check your input and try again."]}


@pytest.mark.django_db
def test_password_update_success():
    """Test for successful password update."""
    user = make_user(email="john.doe@mail.com", password="OldPass1!",
                     is_active=True)
    token = create_knox_token(user, hours=1)
    url = reverse("auth_app:password_update")
    payload = {
        "email": "john.doe@mail.com",
        "password": "NewPass1!",
        "repeated_password": "NewPass1!",
    }
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, payload, format="json")
    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com", "user_id": user.id}
    assert AuthToken.objects.count() == 0
    login_url = reverse("auth_app:login")
    ok = APIClient().post(login_url, {
        "email": "john.doe@mail.com", "password": "NewPass1!"
    }, format="json")
    assert ok.status_code == 200


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
    """Test for password update with missing or invalid data."""
    user = make_user(email="john.doe@mail.com", password="OldPass1!",
                     is_active=True)
    token = create_knox_token(user, hours=1)
    url = reverse("auth_app:password_update")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == BAD


@pytest.mark.django_db
def test_password_update_unauthorized():
    """Test for password update with unauthorized user."""
    url = reverse("auth_app:password_update")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 401
