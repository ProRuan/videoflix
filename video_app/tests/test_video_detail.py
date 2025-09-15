# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from video_app.tests.utils.factories import make_video
from video_progress_app.tests.utils.factories import make_user, make_progress


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


def _auth_headers(user):
    """Get auth headers for logged in user."""
    _, token = AuthToken.objects.create(user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def test_detail_success(api_client, auth_header, db):
    """Test for successful video detail receipt."""
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


def test_detail_unauthorized(api_client):
    """Test for video detail with unauthorized user."""
    url = reverse("video_app:video-detail", kwargs={"pk": 1})
    res = api_client.get(url)
    assert res.status_code == 401


def test_detail_with_progress_fields(api_client, db):
    """Test for video detail including video progress fields."""
    user = make_user()
    video = make_video(title="Bear", genre="Nature")
    prog = make_progress(user, video, last=12.5)
    headers = _auth_headers(user)
    url = reverse("video_app:video-detail", kwargs={"pk": video.id})
    res = api_client.get(url, **headers)
    assert res.status_code == 200
    body = res.json()["video"]
    assert body["progress_id"] == prog.id
    assert body["last_position"] == 12.5


def test_detail_with_last_position(api_client, db):
    """Test for video detail including last_position field."""
    user = make_user()
    video = make_video(title="Bear", genre="Nature")
    make_progress(user, video, last=12.5)
    headers = _auth_headers(user)
    url = reverse("video_app:video-detail", kwargs={"pk": video.id})
    res = api_client.get(url, **headers)
    assert res.status_code == 200
    body = res.json()
    assert body["video"]["last_position"] == 12.5


def test_detail_no_progress(api_client, db):
    """Test for video detail without video progress fields."""
    user = make_user()
    video = make_video(title="Wolf", genre="Nature")
    headers = _auth_headers(user)
    url = reverse("video_app:video-detail", kwargs={"pk": video.id})
    res = api_client.get(url, **headers)
    assert res.status_code == 200
    body = res.json()["video"]
    assert "progress_id" not in body
    assert "last_position" not in body


def test_detail_not_found(api_client, auth_header, db):
    """Test for non-existing video detail."""
    url = reverse("video_app:video-detail", kwargs={"pk": 999999})
    res = api_client.get(url, **auth_header)
    assert res.status_code == 404
