# Standard libraries

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
    user = make_user(email="john.doe@mail.com", password="OldPass1!",
                     is_active=True)
    token = create_knox_token(user, hours=1)
    url = reverse("auth_app:password_update")
    payload = {
        "token": token,
        "email": "john.doe@mail.com",
        "password": "NewPass1!",
        "repeated_password": "NewPass1!",
    }
    res = APIClient().post(url, payload, format="json")

    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com", "user_id": user.id}
    # token used must be deleted
    assert AuthToken.objects.count() == 0

    # verify login works with new password
    login_url = reverse("auth_app:login")
    ok = APIClient().post(
        login_url, {"email": "john.doe@mail.com", "password": "NewPass1!"},
        format="json"
    )
    assert ok.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {},  # all missing
        {"token": ""},  # blank token
        {"token": "bad token", "email": "john.doe@mail.com",
         "password": "NewPass1!", "repeated_password": "NewPass1!"},  # fmt
        {"token": "A"*64, "email": "", "password": "NewPass1!",
         "repeated_password": "NewPass1!"},  # blank email
        {"token": "A"*64, "email": "john", "password": "NewPass1!",
         "repeated_password": "NewPass1!"},  # invalid email
        {"token": "A"*64, "email": "john.doe@mail.com",
         "password": "", "repeated_password": ""},  # blank pw
        {"token": "A"*64, "email": "john.doe@mail.com", "password": "short",
         "repeated_password": "short"},  # too short
        {"token": "A"*64, "email": "john.doe@mail.com", "password": "test123!",
         "repeated_password": "test123!"},  # no uppercase
        {"token": "A"*64, "email": "john.doe@mail.com", "password": "TEST123!",
         "repeated_password": "TEST123!"},  # no lowercase
        {"token": "A"*64, "email": "john.doe@mail.com", "password": "Testabc!",
         "repeated_password": "Testabc!"},  # no digit
        {"token": "A"*64, "email": "john.doe@mail.com", "password": "Test1234",
         "repeated_password": "Test1234"},  # no special
        {"token": "A"*64, "email": "john.doe@mail.com",
         "password": "NewPass1!", "repeated_password": "Other1!"},  # mismatch
    ],
)
@pytest.mark.django_db
def test_password_update_bad_requests(payload):
    user = make_user(email="john.doe@mail.com", password="OldPass1!",
                     is_active=True)
    # token exists but many payloads fail before we use it
    create_knox_token(user, hours=1)
    url = reverse("auth_app:password_update")
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == BAD


@pytest.mark.django_db
def test_password_update_token_not_found():
    make_user(email="john.doe@mail.com", password="OldPass1!",
              is_active=True)
    url = reverse("auth_app:password_update")
    payload = {
        "token": "A"*64,  # looks valid, but not in DB
        "email": "john.doe@mail.com",
        "password": "NewPass1!",
        "repeated_password": "NewPass1!",
    }
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 404


@pytest.mark.django_db
def test_password_update_expired_token_returns_400():
    user = make_user(email="john.doe@mail.com", password="OldPass1!",
                     is_active=True)
    token = create_knox_token(user, hours=-1)  # already expired
    url = reverse("auth_app:password_update")
    payload = {
        "token": token,
        "email": "john.doe@mail.com",
        "password": "NewPass1!",
        "repeated_password": "NewPass1!",
    }
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == BAD
