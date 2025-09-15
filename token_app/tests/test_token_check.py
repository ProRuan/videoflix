# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token


@pytest.mark.django_db
def test_token_check_success():
    """Test for successful token check."""
    user = make_user(email="john.doe@mail.com", is_active=True)
    token = create_knox_token(user, hours=12)
    url = reverse("token_app:token_check")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, data={}, format="json")
    assert res.status_code == 200
    assert res.json() == {
        "token": token, "email": "john.doe@mail.com", "user_id": user.id
    }


@pytest.mark.django_db
def test_token_check_unauthorized():
    """Test for token check with unauthorized status."""
    url = reverse("token_app:token_check")
    res = APIClient().post(url, data={}, format="json")
    assert res.status_code == 401
