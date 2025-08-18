import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()

successful_registration_data = {
    'email': 'user@example.com',
    'password': 'StrongP@ss1',
    'repeated_password': 'StrongP@ss1'
}

invalid_password_data = {
    'email': 'user2@example.com',
    'password': 'weak',
    'repeated_password': 'weak'
}

password_mismatch_data = {
    'email': 'user3@example.com',
    'password': 'StrongP@ss1',
    'repeated_password': 'DifferentP@ss2'
}

bad_request_response = 'Please check your data and try it again.'


@pytest.mark.django_db
class TestRegistrationEndpoint:
    endpoint = reverse('registration')

    def test_registration_success(self):
        client = APIClient()
        data = successful_registration_data.copy()
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 201
        content = response.json()
        # token should be included in the response (activation token)
        assert 'token' in content
        assert content['email'] == data['email']
        assert isinstance(content['user_id'], int)
        user = User.objects.get(email=data['email'])
        # created user should be inactive until activation
        assert user.is_active is False

    def test_registration_invalid_email(self):
        client = APIClient()
        data = successful_registration_data.copy()
        data['email'] = 'invalid-email'
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_registration_invalid_password(self):
        client = APIClient()
        data = invalid_password_data.copy()
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_registration_password_mismatch(self):
        client = APIClient()
        data = password_mismatch_data.copy()
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_confirmation_email_sent(self):
        client = APIClient()
        data = successful_registration_data.copy()
        data['email'] = 'user4@example.com'
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 201
        # Email should be sent (use console backend in dev or check outbox in tests)
        assert len(mail.outbox) == 1
        assert data['email'] in mail.outbox[0].to

    def test_registration_duplicate_email(self):
        User.objects.create_user(
            email='user@example.com', password='StrongP@ss1')
        client = APIClient()
        data = {
            'email': 'user@example.com',
            'password': 'StrongP@ss1',
            'repeated_password': 'StrongP@ss1',
        }
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response
