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
        self.original_token = token

    def test_activation_success(self):
        client = APIClient()
        response = client.post(self.activation_endpoint, {
                               'token': self.original_token.key}, format='json')
        assert response.status_code == 200
        body = response.json()
        assert body.get('email') == self.user.email
        assert body.get('user_id') == self.user.id
        assert 'token' in body

        returned_token_key = body.get('token')
        # the returned token should be different from the original token
        assert returned_token_key != self.original_token.key

        # user should be active
        self.user.refresh_from_db()
        assert self.user.is_active is True

        # original token should have been deleted (consumed)
        assert not Token.objects.filter(key=self.original_token.key).exists()

        # returned token must exist and belong to the user
        assert Token.objects.filter(
            key=returned_token_key, user=self.user).exists()

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
