# Standard libraries
import re

# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user

HEX64 = re.compile(r"^[0-9a-f]{64}$")


@pytest.mark.django_db
def test_login_success_returns_token_email_user_id():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:login")
    res = APIClient().post(url, {
        "email": "john.doe@mail.com", "password": "Test123!"
    }, format="json")

    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["user_id"] == user.id
    assert HEX64.match(res.data["token"])


@pytest.mark.django_db
def test_login_missing_email_returns_400():
    url = reverse("auth_app:login")
    res = APIClient().post(url, {"password": "Test123!"}, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_login_invalid_email_returns_400():
    make_user("john.doe@mail.com")
    url = reverse("auth_app:login")
    res = APIClient().post(url, {
        "email": "john..doe@@mail", "password": "Test123!"
    }, format="json")
    assert res.status_code == 400
    assert "Enter a valid email address." in res.data["detail"]


@pytest.mark.django_db
def test_login_missing_password_returns_400():
    make_user("john.doe@mail.com")
    url = reverse("auth_app:login")
    res = APIClient().post(url, {"email": "john.doe@mail.com"}, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_login_invalid_password_returns_400():
    make_user("john.doe@mail.com")
    url = reverse("auth_app:login")
    res = APIClient().post(url, {
        "email": "john.doe@mail.com", "password": "Wrong123!"
    }, format="json")
    assert res.status_code == 400
    assert "" in res.data["detail"]
