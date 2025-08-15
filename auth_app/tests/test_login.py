# tests/test_login.py
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
        # create an active user for the success case
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_login_success(self):
        """
        Ensure valid credentials return 200 and contain token, email and user_id.
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
        Ensure login with non-existent email returns 400 with generic detail.
        """
        client = APIClient()
        data = {'email': 'wrong@example.com', 'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_invalid_password(self):
        """
        Ensure login with wrong password returns 400 with generic detail.
        """
        client = APIClient()
        data = {'email': 'user@example.com', 'password': 'WrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_missing_email(self):
        """
        Ensure missing email field returns 400 with generic detail.
        """
        client = APIClient()
        data = {'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_missing_password(self):
        """
        Ensure missing password field returns 400 with generic detail.
        """
        client = APIClient()
        data = {'email': 'user@example.com'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_inactive_user(self):
        """
        Ensure an inactive (not yet activated) user cannot log in.
        """
        # create an inactive user
        inactive = User.objects.create_user(
            email='inactive@example.com',
            password='StrongP@ss1',
            is_active=False
        )
        client = APIClient()
        data = {'email': 'inactive@example.com', 'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'
