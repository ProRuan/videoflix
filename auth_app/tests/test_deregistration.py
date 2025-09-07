# Standard libraries
import re

# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user
from token_app.models import Token
from token_app.tests.utils.factories import make_token

HEX64 = re.compile(r"[0-9a-f]{64}")


@pytest.mark.django_db
def test_deregistration_success_sends_deletion_email_and_token():
    user = make_user("john.doe@mail.com")
    auth_tok = make_token(user, Token.TYPE_AUTH, hours_delta=12)
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {
        "token": auth_tok.value,
        "email": user.email,
        "password": "Test123!",
    }, format="json")

    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["user_id"] == user.id

    # new deletion token exists and is unique per rules
    qs = Token.objects.filter(user=user, type=Token.TYPE_DELETION)
    assert qs.count() == 1
    # email sent with 64-hex token in link
    assert len(mail.outbox) == 1
    html = mail.outbox[0].alternatives[0][0]
    assert "http://localhost:4200/delete-account/" in html
    assert HEX64.search(html)


@pytest.mark.django_db
def test_deregistration_missing_token_returns_400():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {
        "email": user.email, "password": "Test123!",
    }, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_deregistration_invalid_token_pattern_returns_400():
    user = make_user("john.doe@mail.com")
    _ = make_token(user, Token.TYPE_AUTH, hours_delta=12)
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {
        "token": "z"*64, "email": user.email, "password": "Test123!",
    }, format="json")
    assert res.status_code == 400
    assert "Invalid token" in res.data["detail"]


@pytest.mark.django_db
def test_deregistration_token_not_found_returns_404():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {
        "token": "a"*64, "email": user.email, "password": "Test123!",
    }, format="json")
    assert res.status_code == 404
    assert "Token not found" in res.data["detail"]


@pytest.mark.django_db
def test_deregistration_invalid_email_returns_400():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_AUTH, hours_delta=12)
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {
        "token": tok.value, "email": "john..doe@@mail", "password": "Test123!",
    }, format="json")
    assert res.status_code == 400
    assert "Enter a valid email address." in res.data["detail"]


@pytest.mark.django_db
def test_deregistration_email_not_matching_token_user_returns_400():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_AUTH, hours_delta=12)
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {
        "token": tok.value, "email": "other@mail.com", "password": "Test123!",
    }, format="json")
    assert res.status_code == 400
    assert "Invalid email" in res.data["detail"]


@pytest.mark.django_db
def test_deregistration_invalid_password_returns_400():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_AUTH, hours_delta=12)
    url = reverse("auth_app:deregistration")
    res = APIClient().post(url, {
        "token": tok.value, "email": user.email, "password": "Wrong123!",
    }, format="json")
    assert res.status_code == 400
    assert "Invalid data" in res.data["detail"]
