# Standard libraries

# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user
from auth_app.utils import create_knox_token

User = get_user_model()


@pytest.mark.django_db
def test_account_deletion_success():
    user = make_user(email="john.doe@mail.com", password="Test123!",
                     is_active=True)
    token = create_knox_token(user, hours=24)
    url = reverse("auth_app:account_deletion")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    res = client.post(url, data={}, format="json")

    assert res.status_code == 204
    assert not User.objects.filter(pk=user.pk).exists()
    assert AuthToken.objects.count() == 0


@pytest.mark.django_db
def test_account_deletion_unauthorized():
    url = reverse("auth_app:account_deletion")
    res = APIClient().post(url, data={}, format="json")
    assert res.status_code == 401
