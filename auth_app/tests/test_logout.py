# Standard libraries

# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from token_app.models import Token
from token_app.tests.utils.factories import make_token, make_user


@pytest.mark.django_db
def test_logout_success_marks_token_used_and_returns_user():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_AUTH, hours_delta=12, used=False)
    url = reverse("auth_app:logout")
    res = APIClient().post(url, {"token": tok.value}, format="json")

    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["user_id"] == user.id
    tok.refresh_from_db()
    assert tok.used is True


@pytest.mark.django_db
def test_logout_missing_token_returns_400():
    url = reverse("auth_app:logout")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_logout_invalid_token_pattern_returns_400():
    user = make_user("john.doe@mail.com")
    _ = make_token(user, Token.TYPE_AUTH, hours_delta=12)
    bad = "z" * 64
    url = reverse("auth_app:logout")
    res = APIClient().post(url, {"token": bad}, format="json")
    assert res.status_code == 400
    assert "Invalid token" in res.data["detail"]


@pytest.mark.django_db
def test_logout_token_not_found_returns_404():
    url = reverse("auth_app:logout")
    res = APIClient().post(url, {"token": "a" * 64}, format="json")
    assert res.status_code == 404
    assert "Token not found" in res.data["detail"]
