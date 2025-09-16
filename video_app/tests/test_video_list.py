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


def _list_url() -> str:
    """Get video list URL."""
    return reverse("video_app:video-list")


def _auth_headers_for(email="user@mail.com"):
    """Get auth headers for specific user."""
    User = get_user_model()
    u = User.objects.create_user(email=email, password="Pwd12345!")
    _, token = AuthToken.objects.create(user=u)
    return u, {"HTTP_AUTHORIZATION": f"Token {token}"}


def _section(payload, name: str):
    """Get video list section."""
    return next((g for g in payload if g["genre"] == name), None)


def _make_at(title: str, genre: str, days_ago: int):
    """Make a video with created_at field."""
    when = timezone.now() - timedelta(days=days_ago)
    return make_video(title=title, genre=genre, created_at=when)


def test_list_unauthorized(api_client):
    """Test for video list with unauthorized user."""
    assert api_client.get(_list_url()).status_code == 401


def test_list_grouped_and_new_section(api_client, db):
    """Test video list with groups and "new" section."""
    _make_at("A", "Sci-Fi", 10)
    _make_at("B", "Drama", 10)
    _make_at("C", "Drama", 200)
    _, headers = _auth_headers_for()
    res = api_client.get(_list_url(), **headers)
    payload = res.json()
    assert res.status_code == 200 and payload[0]["genre"] == "New on Videoflix"
    genres = [g["genre"] for g in payload[1:]]
    titles = {v["title"] for g in payload for v in g.get("videos", [])}
    assert genres == sorted(genres) and titles == {"A", "B", "C"}


def test_list_progress_fields_appear_only_for_started(api_client, db):
    """Test video list with optional progress fields."""
    now = timezone.now()
    v1 = Video.objects.create(title="A", genre="Drama", created_at=now,
                              duration=100.0)
    user, headers = _auth_headers_for()
    VideoProgress.objects.create(user=user, video=v1,
                                 last_position=10.0, relative_position=10.0)
    payload = api_client.get(_list_url(), **headers).json()
    started = _section(payload, "Started videos")["videos"]
    drama = _section(payload, "Drama")["videos"]
    items = {v["title"]: v for v in drama}
    assert [v["title"] for v in started] == ["A"]
    assert "progress_id" in items["A"] and "relative_position" in items["A"]
