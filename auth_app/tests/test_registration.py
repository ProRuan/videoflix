# Third-party suppliers
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
    """
    Provides some tests for the registration endpoint.
    """
    endpoint = reverse('registration')

    def test_registration_success(self):
        """
        Ensure valid data creates a user (status code 201).
        The success response returns token, email and user_id.
        """
        client = APIClient()
        data = successful_registration_data
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 201
        content = response.json()
        assert 'token' in content
        assert content['email'] == data['email']
        assert isinstance(content['user_id'], int)
        user = User.objects.get(email=data['email'])
        assert user.is_active is True

    def test_registration_invalid_email(self):
        """
        Ensure invalid email returns status code 400.
        The response returns a generic error.
        """
        client = APIClient()
        data = successful_registration_data
        data['email'] = 'invalid-email'
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_registration_invalid_password(self):
        """
        Ensure weak password returns status code 400.
        The response returns a generic error.
        """
        client = APIClient()
        data = invalid_password_data
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_registration_password_mismatch(self):
        """
        Ensure mismatched passwords return status code 400.
        The response returns a generic error.
        """
        client = APIClient()
        data = password_mismatch_data
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == bad_request_response

    def test_confirmation_email_sent(self):
        """
        Ensure a confirmation email is sent upon successful registration.
        """
        client = APIClient()
        data = successful_registration_data
        data['email'] = 'user4@example.com'
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 201
        assert len(mail.outbox) == 1
        assert data['email'] in mail.outbox[0].to

    def test_registration_duplicate_email(self):
        """
        Ensure duplicate email registration returns status code 400.
        The response returns a generic error.
        """
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
