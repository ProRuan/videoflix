import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db, django_user_model):
    """
    Create a test user in the database.
    """
    return django_user_model.objects.create(
        email="existing@example.com",
        password="testpassword123"
    )


@pytest.mark.django_db
class TestEmailCheckEndpoint:
    url = '/api/email-check/'

    def test_email_check_email_exists(self, api_client, user):
        # Given an existing user email
        data = {'email': user.email}

        # When POSTing to the endpoint
        response = api_client.post(self.url, data, format='json')

        # Then expect a 404 response because email is already registered
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Accept either a field-level error or a general detail message
        assert 'email' in response.data or 'detail' in response.data

    def test_email_check_email_available(self, api_client):
        # Given an email that does not exist
        data = {'email': 'newuser@example.com'}

        # When POSTing to the endpoint
        response = api_client.post(self.url, data, format='json')

        # Then expect a 200 OK and a simple success message
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('status') == 'ok'

    @pytest.mark.parametrize("payload, expected_errors", [
        ({}, ['email']),  # missing email
        ({'email': 'not-an-email'}, ['email']),  # invalid email format
    ])
    def test_email_check_invalid_request(self, api_client, payload, expected_errors):
        # When POSTing invalid or incomplete data
        response = api_client.post(self.url, payload, format='json')

        # Then expect a 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        for field in expected_errors:
            assert field in response.data
