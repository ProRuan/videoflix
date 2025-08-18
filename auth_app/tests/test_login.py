import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestLoginEndpoint:
    endpoint = reverse('login')

    def setup_method(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongP@ss1'
        )

    def test_login_success(self):
        client = APIClient()
        data = {'email': 'user@example.com', 'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')

        assert response.status_code == 200
        content = response.json()
        assert 'token' in content
        assert content['email'] == self.user.email
        assert content['user_id'] == self.user.id

    def test_login_invalid_email(self):
        client = APIClient()
        data = {'email': 'wrong@example.com', 'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_invalid_password(self):
        client = APIClient()
        data = {'email': 'user@example.com', 'password': 'WrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_missing_email(self):
        client = APIClient()
        data = {'password': 'StrongP@ss1'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_missing_password(self):
        client = APIClient()
        data = {'email': 'user@example.com'}
        response = client.post(self.endpoint, data, format='json')
        assert response.status_code == 400
        assert response.json().get('detail') == 'Please check your data and try it again.'

    def test_login_inactive_user(self):
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
