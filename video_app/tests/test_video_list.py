# Standard libraries
from datetime import timedelta

# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
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


def test_list_unauthorized(api_client):
    url = reverse("video_app:video-list")
    res = api_client.get(url)
    assert res.status_code == 401


def test_list_grouped_and_new_section(api_client, auth_header, db):
    now = timezone.now()
    recent = now - timedelta(days=10)
    older = now - timedelta(days=200)

    make_video(title="A", genre="Sci-Fi", created_at=recent)
    make_video(title="B", genre="Drama", created_at=recent)
    make_video(title="C", genre="Drama", created_at=older)

    url = reverse("video_app:video-list")
    res = api_client.get(url, **auth_header)
    assert res.status_code == 200

    payload = res.json()
    assert isinstance(payload, list)
    assert payload[0]["genre"] == "New on Videoflix"

    # Check genres (excluding the "New" section) are sorted
    genres = [g["genre"] for g in payload[1:]]
    assert genres == sorted(genres)

    # Videos appear across sections
    titles = {v["title"] for g in payload for v in g.get("videos", [])}
    assert titles == {"A", "B", "C"}
