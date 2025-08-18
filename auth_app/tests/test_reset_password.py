import pytest
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from rest_framework.authtoken.models import Token as AuthToken
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from token_app.utils import create_token_for_user
from token_app.models import PasswordResetToken

User = get_user_model()

bad_request_response = 'Please check your data and try it again.'


def get_data(token, email, password, repeated_password):
    return {
        'token': token,
        'email': email,
        'password': password,
        'repeated_password': repeated_password
    }


@pytest.mark.django_db
class TestResetPasswordEndpoint:
    endpoint = reverse('reset-password')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )
        # create a password reset token via token_app
        self.reset_inst = create_token_for_user(self.user, "password_reset")

    def test_reset_password_success(self):
        client = APIClient()
        data = get_data(self.reset_inst.token,
                        self.user.email, 'NewP@ssw0rd', 'NewP@ssw0rd')
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        content = response.json()
        assert 'token' in content
        assert content['email'] == self.user.email
        assert content['user_id'] == self.user.id

        returned_token_key = content['token']
        # returned token should be a DRF auth token for the user
        assert AuthToken.objects.filter(key=returned_token_key, user=self.user).exists()

        # reset token must be marked used
        self.reset_inst.refresh_from_db()
        assert self.reset_inst.used is True

        # authenticate with new password
        user = authenticate(email=self.user.email, password='NewP@ssw0rd')
        assert user is not None and user.is_active

    def test_reset_password_invalid_password(self):
        client = APIClient()
        data = get_data(self.reset_inst.token,
                        self.user.email, 'weak', 'weak')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_reset_password_mismatch(self):
        client = APIClient()
        data = get_data(self.reset_inst.token, self.user.email,
                        'NewP@ssw0rd', 'DifferentP@ss2')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_reset_password_invalid_token(self):
        client = APIClient()
        data = get_data('invalid-token', self.user.email,
                        'NewP@ssw0rd', 'NewP@ssw0rd')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_reset_password_user_not_found(self):
        client = APIClient()
        data = get_data(self.reset_inst.token,
                        'missing@example.com', 'NewP@ssw0rd', 'NewP@ssw0rd')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 404
        body = response.json()
        assert 'email' in body
        assert body['email'] == ['User not found.']
