# Standard libraries

# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from token_app.models import Token
from token_app.tests.utils.factories import make_token, make_user


@pytest.mark.django_db
def test_account_activation_success_returns_200_marks_used_and_activates():
    user = make_user("john.doe@mail.com")
    user.is_active = False
    user.save(update_fields=["is_active"])
    tok = make_token(user, Token.TYPE_ACTIVATION, hours_delta=24, used=False)

    url = reverse("auth_app:account-activation")
    res = APIClient().post(url, {"token": tok.value}, format="json")

    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["user_id"] == user.id
    # Refresh and verify changes
    tok.refresh_from_db()
    user.refresh_from_db()
    assert tok.used is True
    assert user.is_active is True


@pytest.mark.django_db
def test_account_activation_missing_token_returns_400():
    url = reverse("auth_app:account-activation")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_account_activation_invalid_token_returns_400():
    user = make_user("john.doe@mail.com")
    _ = make_token(user, Token.TYPE_ACTIVATION, hours_delta=24)
    bad = "z" * 64  # not hex
    url = reverse("auth_app:account-activation")
    res = APIClient().post(url, {"token": bad}, format="json")
    assert res.status_code == 400
    assert "Invalid token" in res.data["detail"]


@pytest.mark.django_db
def test_account_activation_non_existing_token_returns_404():
    url = reverse("auth_app:account-activation")
    res = APIClient().post(url, {"token": "a" * 64}, format="json")
    assert res.status_code == 404
    assert "Token not found" in res.data["detail"]
