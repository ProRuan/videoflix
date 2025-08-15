# tests/test_reset_password.py
# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()

bad_request_response = 'Please check your data and try it again.'


def get_data(self, email, password, repeated_password):
    """
    Get data containing email, password and repeated_password.
    """
    return {
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
        # token created during forgot-password flow might exist; create one here to mimic that state
        self.token_obj, _ = Token.objects.get_or_create(user=self.user)

    def test_reset_password_success(self):
        """
        Ensure valid new password updates user's password (status code 200).
        The success response returns email and user_id and any existing token is removed.
        """
        client = APIClient()
        data = get_data(self, self.user.email, 'NewP@ssw0rd', 'NewP@ssw0rd')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 200
        content = response.json()
        assert content['email'] == self.user.email
        assert content['user_id'] == self.user.id

        # password was changed and user can authenticate with the new password
        user = authenticate(email=self.user.email, password='NewP@ssw0rd')
        assert user is not None and user.is_active

        # token used for reset (or any existing token) should have been deleted
        assert not Token.objects.filter(user=self.user).exists()

    def test_reset_password_invalid_password(self):
        """
        Ensure weak password returns status code 400.
        The response returns a generic error.
        """
        client = APIClient()
        data = get_data(self, self.user.email, 'weak', 'weak')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_reset_password_mismatch(self):
        """
        Ensure mismatched passwords return status code 400.
        The response returns a generic error.
        """
        client = APIClient()
        data = get_data(self, self.user.email, 'NewP@ssw0rd', 'DifferentP@ss2')
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response
