# Third-party suppliers
import pytest
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from .utils.factories import make_user, make_video


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    """Get APIClient."""
    return APIClient()


def _auth_headers(user):
    """Get auth headers."""
    _, token = AuthToken.objects.create(user=user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def _url_create():
    """Get URL."""
    return reverse("video_progress_app:video-progress-create")


def _url_detail(pid: int):
    """Get URL detail."""
    return reverse("video_progress_app:video-progress-detail",
                   kwargs={"pk": pid})


def _set_duration(video, seconds: float):
    """Set video duration."""
    video.duration = seconds
    video.save(update_fields=["duration"])


def _create_progress(api_client, user, video, last: float) -> int:
    """Create video progress."""
    res = api_client.post(
        _url_create(), {"video_id": video.id, "last_position": last},
        **_auth_headers(user),
    )
    return res.json()["id"]


def test_video_progress_create_success(api_client):
    """Test for successful video progress creation."""
    user, video = make_user(), make_video()
    res = api_client.post(
        _url_create(), {"video_id": video.id, "last_position": 33.3},
        **_auth_headers(user),
    )
    assert res.status_code == 201
    assert res.json()["video_id"] == video.id


def test_video_progress_create_unauthorized(api_client):
    """Test for video progress creation with unauthorized user."""
    res = api_client.post(_url_create(), data={})
    assert res.status_code == 401


def test_video_progress_create_missing_last_position(api_client):
    """Test for video progress with missing last_position."""
    user = make_user()
    res = api_client.post(
        _url_create(), {"video_id": 1}, **_auth_headers(user)
    )
    assert res.status_code == 400


def test_video_progress_create_invalid_position(api_client):
    """Test for video progress creation with invalid last position."""
    user, video = make_user(), make_video()
    res = api_client.post(
        _url_create(), {"video_id": video.id, "last_position": -1},
        **_auth_headers(user),
    )
    assert res.status_code == 400


def test_video_progress_create_video_not_found(api_client):
    """Test for video progress creation with non-existing video."""
    user = make_user()
    res = api_client.post(
        _url_create(), {"video_id": 999999, "last_position": 3},
        **_auth_headers(user),
    )
    assert res.status_code == 404


def test_video_progress_create_relative_position(api_client):
    """Test for video progress creation with calculating relative position."""
    user, video = make_user(), make_video()
    _set_duration(video, 100.0)
    res = api_client.post(
        _url_create(), {"video_id": video.id, "last_position": 25},
        **_auth_headers(user),
    )
    body = res.json()
    assert res.status_code == 201
    assert body["last_position"] == 25
    assert body["relative_position"] == 25.0


def test_video_progress_patch_updates_relative_position(api_client):
    """Test for video progress update with relative position."""
    user, video = make_user(), make_video()
    _set_duration(video, 200.0)
    pid = _create_progress(api_client, user, video, 10)
    res = api_client.patch(
        _url_detail(pid), {"last_position": 50}, **_auth_headers(user)
    )
    body = res.json()
    assert res.status_code == 200
    assert body["last_position"] == 50
    assert body["relative_position"] == 25.0
