# tests/test_account_activation.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestAccountActivationEndpoint:
    activation_endpoint = reverse('account-activation')

    def setup_method(self):
        # create inactive user and token
        self.user = User.objects.create_user(
            email='pending@example.com',
            password='StrongP@ss1',
            is_active=False
        )
        token, _ = Token.objects.get_or_create(user=self.user)
        self.token = token

    def test_activation_success(self):
        client = APIClient()
        response = client.post(self.activation_endpoint, {
                               'token': self.token.key}, format='json')
        assert response.status_code == 200
        body = response.json()
        # assert body.get('token') == self.token.key
        assert body.get('email') == self.user.email
        assert body.get('user_id') == self.user.id

        # user should be active
        self.user.refresh_from_db()
        assert self.user.is_active is True

        # token should be deleted
        assert not Token.objects.filter(key=self.token.key).exists()

    def test_activation_missing_token(self):
        client = APIClient()
        response = client.post(self.activation_endpoint, {}, format='json')
        assert response.status_code == 400
        body = response.json()
        assert 'token' in body

    def test_activation_invalid_token(self):
        client = APIClient()
        response = client.post(self.activation_endpoint, {
                               'token': 'does-not-exist'}, format='json')
        assert response.status_code == 404
        body = response.json()
        assert 'token' in body
