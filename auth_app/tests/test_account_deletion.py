# Standard libraries

# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from token_app.models import Token
from token_app.tests.utils.factories import make_token, make_user


@pytest.mark.django_db
def test_account_deletion_success_deletes_user_and_returns_204():
    user = make_user("john.doe@mail.com")
    tok = make_token(user, Token.TYPE_DELETION, hours_delta=24, used=False)
    url = reverse("auth_app:account-deletion")
    res = APIClient().post(url, {"token": tok.value}, format="json")

    assert res.status_code == 204
    User = get_user_model()
    assert not User.objects.filter(id=user.id).exists()
    # token should be gone via FK cascade
    assert not Token.objects.filter(value=tok.value).exists()


@pytest.mark.django_db
def test_account_deletion_missing_token_returns_400():
    url = reverse("auth_app:account-deletion")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_account_deletion_invalid_token_pattern_returns_400():
    user = make_user("john.doe@mail.com")
    _ = make_token(user, Token.TYPE_DELETION, hours_delta=24)
    url = reverse("auth_app:account-deletion")
    res = APIClient().post(url, {"token": "z"*64}, format="json")
    assert res.status_code == 400
    assert "Invalid token" in res.data["detail"]


@pytest.mark.django_db
def test_account_deletion_non_existing_token_returns_404():
    url = reverse("auth_app:account-deletion")
    res = APIClient().post(url, {"token": "a"*64}, format="json")
    assert res.status_code == 404
    assert "Token not found" in res.data["detail"]
