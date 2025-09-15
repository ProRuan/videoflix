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
from video_app.models import Video
from video_progress_app.models import VideoProgress


@pytest.fixture
def api_client() -> APIClient:
    """Get APIClient."""
    return APIClient()


@pytest.fixture
def auth_header(db):
    """Get auth header."""
    User = get_user_model()
    user = User.objects.create_user(email="u@mail.com", password="Pwd12345!")
    _, token = AuthToken.objects.create(user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def _auth_headers_for(email="user@mail.com"):
    """Get auth headers for logged in user."""
    User = get_user_model()
    u = User.objects.create_user(email=email, password="Pwd12345!")
    _, token = AuthToken.objects.create(u)
    return u, {"HTTP_AUTHORIZATION": f"Token {token}"}


def test_list_unauthorized(api_client):
    """Test for video listing with unauthorized user."""
    url = reverse("video_app:video-list")
    res = api_client.get(url)
    assert res.status_code == 401


def test_list_grouped_and_new_section(api_client, auth_header, db):
    """Test for video listing with grouped list and "new" section."""
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
    genres = [g["genre"] for g in payload[1:]]
    assert genres == sorted(genres)
    titles = {v["title"] for g in payload for v in g.get("videos", [])}
    assert titles == {"A", "B", "C"}


def test_list_progress_fields_appear_only_for_started(api_client, db):
    """Test for video listing with video progress fields."""
    now = timezone.now()
    v1 = Video.objects.create(title="A", genre="Drama", created_at=now,
                              duration=100.0)
    v2 = Video.objects.create(title="B", genre="Drama", created_at=now,
                              duration=200.0)
    user, headers = _auth_headers_for()
    VideoProgress.objects.create(user=user, video=v1,
                                 last_position=10.0, relative_position=10.0)
    url = reverse("video_app:video-list")
    res = api_client.get(url, **headers)
    assert res.status_code == 200
    payload = res.json()
    started = next(g for g in payload if g["genre"] == "Started videos")
    titles = [v["title"] for v in started["videos"]]
    assert titles == ["A"]
    item = started["videos"][0]
    assert "progress_id" in item and "relative_position" in item
    drama = next(g for g in payload if g["genre"] == "Drama")
    items = {v["title"]: v for v in drama["videos"]}
    assert "progress_id" in items["A"]
    assert "relative_position" in items["A"]
    assert "progress_id" not in items["B"]
    assert "relative_position" not in items["B"]
