# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token


@pytest.mark.django_db
def test_account_activation_success():
    """Test for successful account activation."""
    user = make_user(email="john.doe@mail.com", is_active=False)
    token = create_knox_token(user, hours=24)
    url = reverse("auth_app:account_activation")
    res = APIClient().post(url, {"token": token}, format="json")
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "john.doe@mail.com"
    assert body["user_id"] == user.id
    assert body["is_active"] is True
    assert AuthToken.objects.count() == 0


@pytest.mark.django_db
def test_account_activation_missing_token():
    """Test for missing account activation token."""
    url = reverse("auth_app:account_activation")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_account_activation_invalid_token():
    """Test for invalid account activation token."""
    url = reverse("auth_app:account_activation")
    res = APIClient().post(url, {"token": "bad token"}, format="json")
    assert res.status_code == 400
    assert res.json() == {"token": ["Invalid token."]}


@pytest.mark.django_db
def test_account_activation_expired_token():
    """Test for expired account activation token."""
    user = make_user(email="john.doe@mail.com", is_active=False)
    token = create_knox_token(user, hours=-1)  # already expired
    url = reverse("auth_app:account_activation")
    res = APIClient().post(url, {"token": token}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_account_activation_not_found():
    """Test for not-existing account activation token."""
    url = reverse("auth_app:account_activation")
    res = APIClient().post(url, {"token": "A"*64}, format="json")
    assert res.status_code == 404
