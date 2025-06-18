import pytest
from django.contrib.auth.models import User
from rest_framework import status

RESET_URL = '/api/reset-password/'


@pytest.mark.django_db
def test_reset_password_success_changes_password_and_returns_token(client):
    """Ensure valid reset changes password and returns new token and user info."""
    email = 'reset@example.com'
    old_pw = 'OldPass123'
    new_pw = 'NewPass123'
    user = User.objects.create_user(
        username='resetuser', email=email, password=old_pw)

    response = client.post(
        RESET_URL,
        data={
            'email': email,
            'password': new_pw,
            'repeated_password': new_pw
        },
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'token' in data
    assert data['username'] == user.username
    assert data['email'] == email
    assert data['user_id'] == user.id

    user.refresh_from_db()
    assert user.check_password(new_pw)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "password, repeated, field",
    [
        ('short', 'short', 'password'),
        ('allletters', 'allletters', 'password'),
        ('12345678', '12345678', 'password'),
        ('Mismatch1', 'Mismatch2', 'non_field_errors'),
    ]
)
def test_reset_password_invalid_data_returns_400(client, password, repeated, field):
    """Ensure weak, mismatched, or invalid reset data is rejected."""
    email = 'exists@example.com'
    User.objects.create_user(username='existsuser',
                             email=email, password='Exists123')

    response = client.post(
        RESET_URL,
        data={
            'email': email,
            'password': password,
            'repeated_password': repeated
        },
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert field in data


@pytest.mark.django_db
def test_reset_password_nonexistent_email_returns_400(client):
    """Ensure reset with non-existent email returns 400."""
    response = client.post(
        RESET_URL,
        data={
            'email': 'nonexistent@example.com',
            'password': 'ValidPass123',
            'repeated_password': 'ValidPass123'
        },
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert 'non_field_errors' in data or 'email' in data
