# tests/test_reset_password.py
# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()

bad_request_response = 'Please check your data and try it again.'


def get_data(token, email, password, repeated_password):
    """
    Get data containing token, email, password and repeated_password.
    """
    return {
        'token': token,
        'email': email,
        'password': password,
        'repeated_password': repeated_password
    }


@pytest.mark.django_db
class TestResetPasswordEndpoint:
    """
    Provides some tests for the reset-password endpoint.
    """
    endpoint = reverse('reset-password')

    def setup_method(self):
        """
        Set up user for reset-password tests.
        """
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )
        # token created during forgot-password flow (reset token)
        self.reset_token_obj, _ = Token.objects.get_or_create(user=self.user)

    def test_reset_password_success(self):
        """
        Ensure valid new password updates user's password (status code 200).
        The success response returns a fresh auth token, email and user_id,
        and old tokens are removed.
        """
        client = APIClient()
        data = get_data(self.reset_token_obj.key,
                        self.user.email, 'NewP@ssw0rd', 'NewP@ssw0rd')
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        content = response.json()
        assert 'token' in content
        assert content['email'] == self.user.email
        assert content['user_id'] == self.user.id

        # The returned token should be the new auth token for the user
        returned_token_key = content['token']
        assert Token.objects.filter(
            key=returned_token_key, user=self.user).exists()

        # The original reset token should have been deleted (consumed)
        assert not Token.objects.filter(key=self.reset_token_obj.key).exists()

        # password was changed and user can authenticate with the new password
        user = authenticate(email=self.user.email, password='NewP@ssw0rd')
        assert user is not None and user.is_active

    def test_reset_password_invalid_password(self):
        """
        Ensure weak password returns status code 400 with generic error.
        """
        client = APIClient()
        data = get_data(self.reset_token_obj.key,
                        self.user.email, 'weak', 'weak')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_reset_password_mismatch(self):
        """
        Ensure mismatched passwords return status code 400 with generic error.
        """
        client = APIClient()
        data = get_data(self.reset_token_obj.key, self.user.email,
                        'NewP@ssw0rd', 'DifferentP@ss2')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_reset_password_invalid_token(self):
        """
        Ensure invalid token returns status code 400 with generic error.
        """
        client = APIClient()
        data = get_data('invalid-token', self.user.email,
                        'NewP@ssw0rd', 'NewP@ssw0rd')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_reset_password_user_not_found(self):
        """
        Ensure non-existent email returns 404 Not Found.
        """
        client = APIClient()
        # use some token but an email that does not exist
        data = get_data(self.reset_token_obj.key,
                        'missing@example.com', 'NewP@ssw0rd', 'NewP@ssw0rd')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 404
        body = response.json()
        assert 'email' in body
        assert body['email'] == ['User not found.']
