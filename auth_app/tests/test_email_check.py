# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user


@pytest.mark.django_db
def test_email_check_success_existing_email_returns_true():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:email-check")
    res = APIClient().post(url, {"email": user.email}, format="json")
    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["exists"] is True


@pytest.mark.django_db
def test_email_check_success_non_existing_email_returns_false():
    url = reverse("auth_app:email-check")
    res = APIClient().post(url, {"email": "no.user@mail.com"}, format="json")
    assert res.status_code == 200
    assert res.data["email"] == "no.user@mail.com"
    assert res.data["exists"] is False


@pytest.mark.django_db
def test_email_check_missing_email_returns_400():
    url = reverse("auth_app:email-check")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 400
    assert "detail" in res.data


@pytest.mark.django_db
def test_email_check_invalid_email_returns_400():
    url = reverse("auth_app:email-check")
    res = APIClient().post(url, {"email": "invalid@@mail..com"}, format="json")
    assert res.status_code == 400
    assert "Enter a valid email address." in res.data["detail"]
