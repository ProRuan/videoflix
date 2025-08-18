import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token as AuthToken
from rest_framework.test import APIClient

from token_app.utils import create_token_for_user
from token_app.models import AccountActivationToken

User = get_user_model()


@pytest.mark.django_db
class TestAccountActivationEndpoint:
    activation_endpoint = reverse('account-activation')

    def setup_method(self):
        # create inactive user and activation token
        self.user = User.objects.create_user(
            email='pending@example.com',
            password='StrongP@ss1',
            is_active=False
        )
        # create_token_for_user returns the token model instance
        self.activation_inst = create_token_for_user(self.user, "activation")

    def test_activation_success(self):
        client = APIClient()
        response = client.post(self.activation_endpoint, {
                               'token': self.activation_inst.token}, format='json')
        assert response.status_code == 200
        body = response.json()
        assert body.get('email') == self.user.email
        assert body.get('user_id') == self.user.id
        assert 'token' in body

        returned_token_key = body.get('token')
        # returned token is a DRF auth token and should exist
        assert AuthToken.objects.filter(
            key=returned_token_key, user=self.user).exists()

        # user should be active
        self.user.refresh_from_db()
        assert self.user.is_active is True

        # activation token should be marked used (not necessarily deleted)
        self.activation_inst.refresh_from_db()
        assert self.activation_inst.used is True

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
