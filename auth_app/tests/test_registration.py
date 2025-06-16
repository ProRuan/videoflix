import pytest
from django.urls import reverse
from rest_framework import status

REGISTRATION_URL = '/api/registration/'


@pytest.mark.django_db
def test_successful_registration(client):
    """Ensure a user can register successfully."""
    payload = {
        "username": "exampleuser",
        "email": "example@mail.de",
        "password": "StrongPass123",
        "repeated_password": "StrongPass123"
    }
    response = client.post(REGISTRATION_URL, data=payload,
                           content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "token" in data
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert isinstance(data["user_id"], int)


@pytest.mark.django_db
@pytest.mark.parametrize("username", ["", "a", "ab"])
def test_invalid_or_short_username(client, username):
    """Ensure invalid or too short usernames are rejected."""
    payload = {
        "username": username,
        "email": "valid@mail.de",
        "password": "StrongPass123",
        "repeated_password": "StrongPass123"
    }
    response = client.post(REGISTRATION_URL, data=payload,
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("email", ["not-an-email", "user@.com", "user.com"])
def test_invalid_email(client, email):
    """Ensure invalid emails are rejected."""
    payload = {
        "username": "validuser",
        "email": email,
        "password": "StrongPass123",
        "repeated_password": "StrongPass123"
    }
    response = client.post(REGISTRATION_URL, data=payload,
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("password", ["123", "pass", "short"])
def test_invalid_password(client, password):
    """Ensure too short or weak passwords are rejected."""
    payload = {
        "username": "validuser",
        "email": "valid@mail.de",
        "password": password,
        "repeated_password": password
    }
    response = client.post(REGISTRATION_URL, data=payload,
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_password_mismatch(client):
    """Ensure mismatched passwords are rejected."""
    payload = {
        "username": "validuser",
        "email": "valid@mail.de",
        "password": "Password123",
        "repeated_password": "Password321"
    }
    response = client.post(REGISTRATION_URL, data=payload,
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
