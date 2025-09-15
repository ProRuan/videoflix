# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token


@pytest.mark.django_db
def test_logout_success():
    """Test for successful logout."""
    user = make_user(email="john.doe@mail.com", is_active=True)
    token = create_knox_token(user, hours=12)
    url = reverse("auth_app:logout")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, data={}, format="json")

    assert res.status_code == 200
    assert res.json() == {"message": ["Logout successful."]}
    assert AuthToken.objects.count() == 0


@pytest.mark.django_db
def test_logout_unauthorized():
    """Test for logout with unauthorized user."""
    url = reverse("auth_app:logout")
    res = APIClient().post(url, data={}, format="json")
    assert res.status_code == 401
