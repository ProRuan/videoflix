# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token


@pytest.mark.django_db
def test_activation_token_check_success():
    """Test for successful account activation check."""
    user = make_user(email="john.doe@mail.com", is_active=False)
    token = create_knox_token(user, hours=24)
    url = reverse("token_app:activation_token_check")
    res = APIClient().post(url, {"token": token}, format="json")
    assert res.status_code == 200
    assert res.json() == {
        "token": token, "email": "john.doe@mail.com", "user_id": user.id
    }


@pytest.mark.parametrize("payload", [{}, {"token": ""}, {"token": "bad token"}])
@pytest.mark.django_db
def test_activation_token_check_bad_request(payload):
    """Test for activation token check with missing or invalid token."""
    url = reverse("token_app:activation_token_check")
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_activation_token_check_expired_token():
    """Test for activation token check with expired token."""
    user = make_user(email="john.doe@mail.com", is_active=False)
    token = create_knox_token(user, hours=-1)
    url = reverse("token_app:activation_token_check")
    res = APIClient().post(url, {"token": token}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_activation_token_check_token_not_found():
    """Test for activation token check with non-existing token."""
    make_user(email="john.doe@mail.com", is_active=False)
    url = reverse("token_app:activation_token_check")
    res = APIClient().post(url, {"token": "A"*64}, format="json")
    assert res.status_code == 404
