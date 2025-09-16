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


def _auth_headers(user):
    """Get auth headers for specific user."""
    _, token = AuthToken.objects.create(user=user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def _detail_url(pk: int) -> str:
    """Get video detail URL."""
    return reverse("video_app:video-detail", kwargs={"pk": pk})


@pytest.fixture
def auth_header(db):
    """Get auth header."""
    User = get_user_model()
    u = User.objects.create_user(email="u@mail.com", password="Pwd12345!")
    return _auth_headers(u)


def test_detail_success(api_client, auth_header, db):
    """Test for successful video detail receipt."""
    v = make_video(title="Wolf", genre="Nature")
    res = api_client.get(_detail_url(v.id), **auth_header)
    body = res.json()["video"]
    assert res.status_code == 200
    assert body["id"] == v.id and body["title"] == "Wolf"
    assert "duration" in body and "quality_levels" in body


def test_detail_unauthorized(api_client):
    """Test for video detail receipt with unauthorized user."""
    assert api_client.get(_detail_url(1)).status_code == 401


def test_detail_with_progress_fields(api_client, db):
    """Test for successful video detail receipt with progress fields."""
    user = make_user()
    video = make_video(title="Bear", genre="Nature")
    prog = make_progress(user, video, last=12.5)
    res = api_client.get(_detail_url(video.id), **_auth_headers(user))
    body = res.json()["video"]
    assert res.status_code == 200
    assert body["progress_id"] == prog.id and body["last_position"] == 12.5


def test_detail_with_last_position(api_client, db):
    """Test for video detail receipt with last position."""
    user = make_user()
    video = make_video(title="Bear", genre="Nature")
    make_progress(user, video, last=12.5)
    res = api_client.get(_detail_url(video.id), **_auth_headers(user))
    assert res.status_code == 200
    assert res.json()["video"]["last_position"] == 12.5


def test_detail_no_progress(api_client, db):
    """Test for video detail receipt without progress fields."""
    user = make_user()
    video = make_video(title="Wolf", genre="Nature")
    res = api_client.get(_detail_url(video.id), **_auth_headers(user))
    body = res.json()["video"]
    assert res.status_code == 200
    assert "progress_id" not in body and "last_position" not in body


def test_detail_not_found(api_client, auth_header, db):
    """Test for non-existing video detail."""
    assert api_client.get(_detail_url(999999), **
                          auth_header).status_code == 404
