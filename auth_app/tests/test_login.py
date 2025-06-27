# Third-party supplier
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestLoginEndpoint:
    """
    Provides some tests for the login endpoint.
    """
    endpoint = reverse('login')

    def setup_method(self):
        """
        Set up user for login tests.
        """
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_login_success(self):
        """
        Ensure valid credentials (status code 200).
        The success response returns token, email and user_id.
        """
        client = APIClient()
        data = {'email': 'user@example.com', 'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 200
        content = response.json()
        assert 'token' in content
        assert content['email'] == self.user.email
        assert content['user_id'] == self.user.id

    def test_login_invalid_email(self):
        """
        Ensure login with non-existent email returns status code 400.
        """
        client = APIClient()
        data = {'email': 'wrong@example.com', 'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400

    def test_login_invalid_password(self):
        """
        Ensure login with wrong password returns status code 400.
        """
        client = APIClient()
        data = {'email': 'user@example.com', 'password': 'WrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
