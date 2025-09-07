# Standard libraries

# Third-party suppliers
import pytest
from django.contrib.auth import authenticate
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user
from token_app.models import Token
from token_app.tests.utils.factories import make_token


@pytest.mark.django_db
def test_password_update_success_changes_password_and_marks_token_used():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_RESET, hours_delta=1, used=False)
    url = reverse("auth_app:password-update")
    payload = {
        "token": tok.value,
        "email": user.email,
        "password": "Test123!",
        "repeated_password": "Test123!",
    }
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["user_id"] == user.id
    tok.refresh_from_db()
    assert tok.used is True
    # authenticate with new password
    assert authenticate(username=user.email, password="Test123!")


@pytest.mark.django_db
def test_password_update_missing_token_returns_400():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:password-update")
    res = APIClient().post(url, {
        "email": user.email, "password": "Test123!",
        "repeated_password": "Test123!",
    }, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_password_update_invalid_token_pattern_returns_400():
    user = make_user("john.doe@mail.com")
    _ = make_token(user, Token.TYPE_RESET, hours_delta=1)
    url = reverse("auth_app:password-update")
    res = APIClient().post(url, {
        "token": "z" * 64, "email": user.email,
        "password": "Test123!", "repeated_password": "Test123!",
    }, format="json")
    assert res.status_code == 400
    assert "Invalid token" in res.data["detail"]


@pytest.mark.django_db
def test_password_update_non_existing_token_returns_404():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:password-update")
    res = APIClient().post(url, {
        "token": "a" * 64, "email": user.email,
        "password": "Test123!", "repeated_password": "Test123!",
    }, format="json")
    assert res.status_code == 404
    assert "Token not found" in res.data["detail"]


@pytest.mark.django_db
def test_password_update_missing_or_invalid_email_returns_400():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_RESET, hours_delta=1)
    url = reverse("auth_app:password-update")

    # missing email
    res1 = APIClient().post(url, {
        "token": tok.value, "password": "Test123!",
        "repeated_password": "Test123!",
    }, format="json")
    assert res1.status_code == 400

    # invalid email format
    res2 = APIClient().post(url, {
        "token": tok.value, "email": "bad@@mail",
        "password": "Test123!", "repeated_password": "Test123!",
    }, format="json")
    assert res2.status_code == 400
    assert "Enter a valid email address." in res2.data["detail"]

    # email not matching token's user
    res3 = APIClient().post(url, {
        "token": tok.value, "email": "other@mail.com",
        "password": "Test123!", "repeated_password": "Test123!",
    }, format="json")
    assert res3.status_code == 400
    assert "Invalid email" in res3.data["detail"]


@pytest.mark.django_db
def test_password_update_missing_or_invalid_password_or_mismatch_returns_400():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_RESET, hours_delta=1)
    url = reverse("auth_app:password-update")

    # missing passwords
    res1 = APIClient().post(url, {"token": tok.value, "email": user.email},
                            format="json")
    assert res1.status_code == 400

    # mismatch
    res2 = APIClient().post(url, {
        "token": tok.value, "email": user.email,
        "password": "Test123!", "repeated_password": "Test123!!",
    }, format="json")
    assert res2.status_code == 400
    assert "invalid data" in res2.data["detail"].lower()

    # weak password
    res3 = APIClient().post(url, {
        "token": tok.value, "email": user.email,
        "password": "weakpass", "repeated_password": "weakpass",
    }, format="json")
    assert res3.status_code == 400
    assert "invalid data" in res3.data["detail"].lower()
