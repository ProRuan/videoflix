import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestForgotPasswordEndpoint:
    endpoint = reverse('forgot-password')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_forgot_password_success(self):
        client = APIClient()
        data = {'email': 'user@example.com'}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        content = response.json()
        assert content.get('email') == self.user.email
        assert content.get('user_id') == self.user.id

        # An email should be sent
        assert len(mail.outbox) == 1
        assert self.user.email in mail.outbox[0].to

    def test_forgot_password_email_not_found(self):
        client = APIClient()
        data = {'email': 'missing@example.com'}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 404
        body = response.json()
        assert 'email' in body or 'detail' in body

    @pytest.mark.parametrize("payload", [
        {},  # missing email
        {'email': 'not-an-email'},  # invalid email format
    ])
    def test_forgot_password_invalid_request(self, payload):
        client = APIClient()
        response = client.post(self.endpoint, payload, format='json')

        assert response.status_code == 400
        body = response.json()
        assert 'detail' in body
