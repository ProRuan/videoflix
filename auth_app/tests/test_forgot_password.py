# Third-party layers
import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()

bad_request_response = 'Please check your data and try it again.'


@pytest.mark.django_db
class TestForgotPasswordEndpoint:
    """
    Provides some tests for the forgot-password endpoint.
    """
    endpoint = reverse('forgot-password')

    def setup_method(self):
        """
        Set up user for forgot-password tests.
        """
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_forgot_password_success(self):
        """
        Ensure valid email succeeds.
        The success response returns token, email, user_id and sends email.
        """
        client = APIClient()
        data = {'email': 'user@example.com'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 200
        content = response.json()
        assert 'token' in content
        assert content['email'] == self.user.email
        assert content['user_id'] == self.user.id
        token = Token.objects.get(user=self.user)
        assert content['token'] == token.key
        assert len(mail.outbox) == 1
        assert self.user.email in mail.outbox[0].to

    def test_forgot_password_invalid_email(self):
        """
        Ensure non-existent email returns status code 400.
        The response returns a generic error.
        """
        client = APIClient()
        data = {'email': 'wrong@example.com'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response
