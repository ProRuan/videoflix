import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestDeregistrationEndpoint:
    endpoint = reverse('deregistration')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_deregistration_success(self):
        client = APIClient()
        data = {'email': 'user@example.com', 'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        content = response.json()
        assert content.get('email') == self.user.email
        assert content.get('user_id') == self.user.id
        assert content.get('token')  # token present and non-empty

        # Email should be sent (confirm-deregistration)
        assert len(mail.outbox) == 1
        assert self.user.email in mail.outbox[0].to

    def test_deregistration_user_not_found(self):
        client = APIClient()
        data = {'email': 'missing@example.com', 'password': 'whatever'}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 404
        body = response.json()
        assert 'email' in body

    @pytest.mark.parametrize("payload, expected_field", [
        ({}, 'email'),  # missing email
        ({'email': 'not-an-email', 'password': 'x'},
         'email'),  # invalid email format
    ])
    def test_deregistration_invalid_request(self, payload, expected_field):
        client = APIClient()
        response = client.post(self.endpoint, payload, format='json')

        assert response.status_code == 400
        body = response.json()
        assert expected_field in body
