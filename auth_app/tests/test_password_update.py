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
        "email": "john.doe@mail.com",
        "password": "NewPass1!",
        "repeated_password": "NewPass1!",
    }
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, payload, format="json")

    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com", "user_id": user.id}
    assert AuthToken.objects.count() == 0  # used token deleted

    # verify login works with new password
    login_url = reverse("auth_app:login")
    ok = APIClient().post(login_url, {
        "email": "john.doe@mail.com", "password": "NewPass1!"
    }, format="json")
    assert ok.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {},  # missing all
        {"email": ""},  # blank email
        {"email": "john"},  # invalid email
        {"email": "john.doe@mail.com"},  # missing passwords
        {"email": "john.doe@mail.com", "password": ""},  # blank pw
        {"email": "john.doe@mail.com", "password": "short",
         "repeated_password": "short"},  # too short
        {"email": "john.doe@mail.com", "password": "test123!",
         "repeated_password": "test123!"},  # no uppercase
        {"email": "john.doe@mail.com", "password": "TEST123!",
         "repeated_password": "TEST123!"},  # no lowercase
        {"email": "john.doe@mail.com", "password": "Testabc!",
         "repeated_password": "Testabc!"},  # no digit
        {"email": "john.doe@mail.com", "password": "Test1234",
         "repeated_password": "Test1234"},  # no special
        {"email": "john.doe@mail.com", "password": "NewPass1!",
         "repeated_password": "Other1!"},  # mismatch
        {"email": "other@mail.com", "password": "NewPass1!",
         "repeated_password": "NewPass1!"},  # email != token user
    ],
)
@pytest.mark.django_db
def test_password_update_bad_request(payload):
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
    url = reverse("auth_app:password_update")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 401
