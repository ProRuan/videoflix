import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestAccountReactivationEndpoint:
    endpoint = reverse('account-reactivation')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='reactivate@example.com',
            password='StrongP@ss1',
            is_active=False  # typical initial state prior to activation/reactivation
        )

    def test_account_reactivation_success(self):
        client = APIClient()
        data = {'email': 'reactivate@example.com'}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        content = response.json()
        # When the email exists the endpoint returns token, email and user_id
        assert content.get('email') == self.user.email
        assert content.get('user_id') == self.user.id
        assert content.get('token') is not None and content.get('token') != ''

        # An email should be sent
        assert len(mail.outbox) == 1
        assert self.user.email in mail.outbox[0].to

    def test_account_reactivation_email_not_found_returns_generic_success(self):
        client = APIClient()
        data = {'email': 'missing-reactivate@example.com'}
        response = client.post(self.endpoint, data, format='json')

        # Security-safe behaviour: return 200 with {"status":"ok"} when email not found
        assert response.status_code == 200
        body = response.json()
        assert body.get('status') == 'ok'

        # No email must be sent for non-existing address
        assert len(mail.outbox) == 0

    @pytest.mark.parametrize("payload, expected_field", [
        ({}, 'email'),  # missing email
        ({'email': 'not-an-email'}, 'email'),  # invalid email format
    ])
    def test_account_reactivation_invalid_request(self, payload, expected_field):
        client = APIClient()
        response = client.post(self.endpoint, payload, format='json')

        assert response.status_code == 400
        body = response.json()
        assert expected_field in body
