# Standard libraries
import re

# Third-party suppliers
import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from token_app.models import Token
from token_app.tests.utils.factories import make_token, make_user

HEX64 = re.compile(r"[0-9a-f]{64}")


@pytest.mark.django_db
def test_account_reactivation_success_sends_email_and_refreshes_token():
    user = make_user("john.doe@mail.com")
    old = make_token(user, Token.TYPE_ACTIVATION, hours_delta=24)
    url = reverse("auth_app:account-reactivation")
    res = APIClient().post(url, {"email": user.email}, format="json")

    assert res.status_code == 200
    assert res.data["email"] == user.email
    assert res.data["user_id"] == user.id
    # Only one active activation token, different from old
    toks = Token.objects.filter(user=user, type=Token.TYPE_ACTIVATION)
    assert toks.count() == 1
    assert toks.first().value != old.value
    # Email was sent with link containing the new token
    assert len(mail.outbox) == 1
    html = mail.outbox[0].alternatives[0][0]
    assert "http://localhost:4200/activate-account/" in html
    assert HEX64.search(html)


@pytest.mark.django_db
def test_account_reactivation_missing_email_returns_400():
    url = reverse("auth_app:account-reactivation")
    res = APIClient().post(url, {}, format="json")
    assert res.status_code == 400
    assert "This field is required." in res.data["detail"]


@pytest.mark.django_db
def test_account_reactivation_invalid_email_returns_400():
    user = make_user("john.doe@mail.com")
    url = reverse("auth_app:account-reactivation")
    res = APIClient().post(url, {"email": "john..doe@@mail"}, format="json")
    assert res.status_code == 400
    assert "Enter a valid email address." in res.data["detail"]


@pytest.mark.django_db
def test_account_reactivation_non_existing_user_returns_404():
    url = reverse("auth_app:account-reactivation")
    res = APIClient().post(url, {"email": "no.user@mail.com"}, format="json")
    assert res.status_code == 404
    assert "User not found" in res.data["detail"]
