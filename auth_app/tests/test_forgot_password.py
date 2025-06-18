import pytest
from django.contrib.auth.models import User
from django.core import mail
from rest_framework import status

FORGOT_URL = '/api/forgot-password/'


@pytest.mark.django_db
def test_forgot_password_success_sends_email_and_returns_email(client):
    """Ensure valid email triggers a reset email and returns the email."""
    email = 'user@example.com'
    User.objects.create_user(
        username='testuser', email=email, password='TestPass123')
    mail.outbox = []

    response = client.post(
        FORGOT_URL,
        data={'email': email},
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get('email') == email

    # Email was queued
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert email in sent.to
    assert 'Reset your Videoflix password' in sent.subject


@pytest.mark.django_db
def test_forgot_password_invalid_email_returns_400(client):
    """Ensure non-existent email returns 400 with error."""
    response = client.post(
        FORGOT_URL,
        data={'email': 'noone@nowhere.com'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert 'email' in data or data.get('non_field_errors')
