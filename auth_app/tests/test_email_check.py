# Standard libraries

# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from auth_app.tests.utils.factories import make_user


@pytest.mark.django_db
def test_email_check_success():
    url = reverse("auth_app:email_check")
    res = APIClient().post(
        url, {"email": "john.doe@mail.com"}, format="json"
    )
    assert res.status_code == 200
    assert res.json() == {"email": "john.doe@mail.com"}


@pytest.mark.parametrize(
    "payload",
    [
        {},  # missing
        {"email": ""},  # blank
        {"email": "john"},  # invalid
        {"email": "john.doe@mail"},  # invalid
        {"email": "john.doe@mail.c"},  # invalid
    ],
)
@pytest.mark.django_db
def test_email_check_bad_request_missing_or_invalid(payload):
    url = reverse("auth_app:email_check")
    res = APIClient().post(url, payload, format="json")
    assert res.status_code == 400
    assert res.json() == {
        "detail": ["Please check your email and try again."]
    }


@pytest.mark.django_db
def test_email_check_already_existing():
    make_user(email="john.doe@mail.com")
    url = reverse("auth_app:email_check")
    res = APIClient().post(
        url, {"email": "john.doe@mail.com"}, format="json"
    )
    assert res.status_code == 400
    assert res.json() == {
        "detail": ["Please check your email and try again."]
    }
