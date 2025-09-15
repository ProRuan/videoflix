# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

# Local imports
from auth_app.tests.utils.factories import make_user


@pytest.mark.django_db
def test_account_reactivation_success_existing_email():
    """Test for successful account reactivation with existing email."""
    user = make_user(email="john.doe@mail.com", is_active=False)
    url = reverse("auth_app:account_reactivation")
    res = APIClient().post(url, {"email": "john.doe@mail.com"}, format="json")
    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com"}
    assert len(mail.outbox) == 1
    assert "Activate your account" in mail.outbox[0].subject
    assert AuthToken.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_account_reactivation_success_non_existing_email():
    """Test for successful account reactivation with non-existing email."""
    url = reverse("auth_app:account_reactivation")
    res = APIClient().post(url, {"email": "nobody@mail.com"}, format="json")
    assert res.status_code == 200
    assert res.json() == {"email": "nobody@mail.com"}
    assert len(mail.outbox) == 0
    assert AuthToken.objects.count() == 0


@pytest.mark.parametrize(
    "bad,err",
    [
        ("", {"email": ["This field may not be blank."]}),
        ("john", {"email": ["Enter a valid email address."]}),
        ("john.doe@mail", {"email": ["Enter a valid email address."]}),
        ("john.doe@mail.c", {"email": ["Enter a valid email address."]}),
    ],
)
@pytest.mark.django_db
def test_account_reactivation_invalid_or_missing_email(bad, err):
    """Test for account reactivation with missing or invalid email."""
    url = reverse("auth_app:account_reactivation")
    res = APIClient().post(url, {"email": bad}, format="json")
    assert res.status_code == 400
    assert res.json() == err
