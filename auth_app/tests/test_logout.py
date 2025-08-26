import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token as AuthToken

User = get_user_model()


@pytest.mark.django_db
class TestLogoutEndpoint:
    endpoint = reverse('logout')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_logout_success(self):
        token = AuthToken.objects.create(user=self.user)
        client = APIClient()
        data = {'token': token.key}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 204
        # token should be deleted
        assert not AuthToken.objects.filter(key=token.key).exists()

    def test_logout_missing_fields(self):
        # omit token
        client = APIClient()
        data = {}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        # ensure field-level error for token exists
        assert 'token' in response.json()

    def test_logout_token_not_found(self):
        client = APIClient()
        data = {'token': 'nonexistenttoken'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 404
