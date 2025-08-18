import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create(
        email="existing@example.com",
        password="testpassword123"
    )


@pytest.mark.django_db
class TestEmailCheckEndpoint:
    url = '/api/email-check/'

    def test_email_check_email_exists(self, api_client, user):
        data = {'email': user.email}
        response = api_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'email' in response.data or 'detail' in response.data

    def test_email_check_email_available(self, api_client):
        data = {'email': 'newuser@example.com'}
        response = api_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('status') == 'ok'

    @pytest.mark.parametrize("payload, expected_errors", [
        ({}, ['email']),
        ({'email': 'not-an-email'}, ['email']),
    ])
    def test_email_check_invalid_request(self, api_client, payload, expected_errors):
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        for field in expected_errors:
            assert field in response.data
