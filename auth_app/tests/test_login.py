import pytest
from django.contrib.auth.models import User
from rest_framework import status

LOGIN_URL = "/api/login/"


@pytest.mark.django_db
def test_successful_login(client):
    """Ensure a user can log in with valid credentials."""
    user = User.objects.create_user(
        username="exampleUsername", email="example@mail.de", password="examplePassword")
    response = client.post(LOGIN_URL, data={
        "username": "exampleUsername",
        "password": "examplePassword"
    }, content_type="application/json")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "token" in data
    assert data["username"] == "exampleUsername"
    assert data["email"] == "example@mail.de"
    assert data["user_id"] == user.id


@pytest.mark.django_db
@pytest.mark.parametrize("username", ["", "a", "ab", "unknownUser"])
def test_invalid_or_short_username(client, username):
    """Ensure login fails for invalid or too short usernames."""
    User.objects.create_user(username="validUser", password="validPassword")
    response = client.post(LOGIN_URL, data={
        "username": username,
        "password": "validPassword"
    }, content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_invalid_password(client):
    """Ensure login fails for wrong password."""
    User.objects.create_user(username="exampleUsername",
                             password="correctPassword")
    response = client.post(LOGIN_URL, data={
        "username": "exampleUsername",
        "password": "wrongPassword"
    }, content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
