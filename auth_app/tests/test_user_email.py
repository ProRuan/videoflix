import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token as AuthToken

User = get_user_model()


@pytest.mark.django_db
class TestUserEmailEndpoint:
    endpoint = reverse('user-email')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_user_email_success(self):
        token = AuthToken.objects.create(user=self.user)
        client = APIClient()
        data = {'token': token.key}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        content = response.json()
        assert content.get('email') == self.user.email

    def test_user_email_missing_token(self):
        client = APIClient()
        data = {}  # missing token
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        # Ensure field-level error for token exists
        assert 'token' in response.json()

    def test_user_email_token_not_found(self):
        client = APIClient()
        data = {'token': 'nonexistenttoken'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 404

    def test_user_email_token_belongs_to_different_user(self):
        # create token for another user and verify we get that user's email
        other = User.objects.create_user(
            email='other@example.com', password='OtherP@ss1')
        token = AuthToken.objects.create(user=other)
        client = APIClient()
        data = {'token': token.key}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        assert response.json().get('email') == other.email
