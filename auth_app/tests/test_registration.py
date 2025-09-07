# Standard libraries

# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user


@pytest.mark.django_db
def test_registration_success_returns_201_and_sends_email():
    client = APIClient()
    url = reverse("auth_app:registration")
    payload = {
        "email": "john.doe@mail.com",
        "password": "Test123!",
        "repeated_password": "Test123!",
    }
    res = client.post(url, payload, format="json")
    assert res.status_code == 201
    assert res.data["email"] == "john.doe@mail.com"
    assert "user_id" in res.data
    assert len(mail.outbox) == 1
    assert "Confirm your email" in mail.outbox[0].subject


@pytest.mark.django_db
def test_registration_fails_on_missing_email():
    client = APIClient()
    url = reverse("auth_app:registration")
    res = client.post(url, {"password": "Test123!",
                      "repeated_password": "Test123!"})
    assert res.status_code == 400


@pytest.mark.django_db
def test_registration_fails_on_invalid_email():
    client = APIClient()
    url = reverse("auth_app:registration")
    bad = "john.doe@@mail..com"
    res = client.post(url, {"email": bad, "password": "Test123!",
                            "repeated_password": "Test123!"})
    assert res.status_code == 400


@pytest.mark.django_db
def test_registration_fails_on_existing_email():
    make_user("john.doe@mail.com")
    client = APIClient()
    url = reverse("auth_app:registration")
    res = client.post(url, {"email": "john.doe@mail.com",
                            "password": "Test123!",
                            "repeated_password": "Test123!"})
    assert res.status_code == 400


@pytest.mark.django_db
def test_registration_fails_on_missing_or_weak_passwords():
    client = APIClient()
    url = reverse("auth_app:registration")
    # Missing repeated_password
    res1 = client.post(url, {"email": "a@mail.com", "password": "Test123!"})
    assert res1.status_code == 400
    # Weak password
    res2 = client.post(url, {"email": "b@mail.com", "password": "test1234",
                             "repeated_password": "test1234"})
    assert res2.status_code == 400


@pytest.mark.django_db
def test_registration_fails_on_password_mismatch():
    client = APIClient()
    url = reverse("auth_app:registration")
    res = client.post(url, {"email": "a@mail.com", "password": "Test123!",
                            "repeated_password": "Test123!!"})
    assert res.status_code == 400
