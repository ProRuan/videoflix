# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from .utils.factories import make_video


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def auth_header(db):
    User = get_user_model()
    user = User.objects.create_user(email="u@mail.com", password="Pwd12345!")
    _, token = AuthToken.objects.create(user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def test_detail_unauthorized(api_client):
    url = reverse("video_app:video-detail", kwargs={"pk": 1})
    res = api_client.get(url)
    assert res.status_code == 401


def test_detail_success(api_client, auth_header, db):
    v = make_video(title="Wolf", genre="Nature")
    url = reverse("video_app:video-detail", kwargs={"pk": v.id})
    res = api_client.get(url, **auth_header)
    assert res.status_code == 200
    body = res.json()
    assert "video" in body
    assert body["video"]["id"] == v.id
    assert body["video"]["title"] == "Wolf"
    assert "duration" in body["video"]
    assert "quality_levels" in body["video"]


def test_detail_not_found(api_client, auth_header, db):
    url = reverse("video_app:video-detail", kwargs={"pk": 999999})
    res = api_client.get(url, **auth_header)
    assert res.status_code == 404
