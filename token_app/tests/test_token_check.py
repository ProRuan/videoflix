# Standard libraries

# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from token_app.models import Token
from token_app.tests.utils.factories import make_token, make_user


@pytest.mark.django_db
def test_token_check_success_returns_200():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_ACTIVATION, hours_delta=24)
    res = APIClient().post(reverse("token_app:check"),
                           {"token": tok.value}, format="json")
    assert res.status_code == 200
    assert res.data["token"] == tok.value
    assert res.data["email"] == user.email
    assert res.data["user_id"] == user.id


@pytest.mark.django_db
def test_token_check_missing_token_returns_400():
    res = APIClient().post(reverse("token_app:check"), {}, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_token_check_invalid_pattern_returns_400():
    user = make_user("john.doe@mail.com")
    _ = make_token(user, Token.TYPE_RESET, hours_delta=1)
    bad = "z" * 64
    res = APIClient().post(reverse("token_app:check"),
                           {"token": bad}, format="json")
    assert res.status_code == 400
    assert "Invalid token pattern" in res.data["detail"]


@pytest.mark.django_db
def test_token_check_expired_returns_400():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_RESET, hours_delta=-1)
    res = APIClient().post(reverse("token_app:check"),
                           {"token": tok.value}, format="json")
    assert res.status_code == 400
    assert "expired" in res.data["detail"].lower()


@pytest.mark.django_db
def test_token_check_used_returns_400():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_DELETION, hours_delta=24, used=True)
    res = APIClient().post(reverse("token_app:check"),
                           {"token": tok.value}, format="json")
    assert res.status_code == 400
    assert "used" in res.data["detail"].lower()


@pytest.mark.django_db
def test_token_check_non_existing_token_returns_404():
    res = APIClient().post(reverse("token_app:check"),
                           {"token": "a" * 64}, format="json")
    assert res.status_code == 404
    assert "Token not found" in res.data["detail"]


@pytest.mark.django_db
def test_token_check_user_deleted_returns_404():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_AUTH, hours_delta=12)
    user.delete()
    res = APIClient().post(reverse("token_app:check"),
                           {"token": tok.value}, format="json")
    assert res.status_code == 404
    assert "Token not found" in res.data["detail"]
