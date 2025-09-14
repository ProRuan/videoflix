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
    return APIClient()


def _auth_headers(user):
    _, token = AuthToken.objects.create(user=user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def _url_create():
    return reverse("video_progress_app:video-progress-create")


def _url_detail(pid: int):
    return reverse("video_progress_app:video-progress-detail",
                   kwargs={"pk": pid})


def _set_duration(video, seconds: float):
    video.duration = seconds
    video.save(update_fields=["duration"])


def _create_progress(api_client, user, video, last: float) -> int:
    res = api_client.post(
        _url_create(), {"video_id": video.id, "last_position": last},
        **_auth_headers(user),
    )
    return res.json()["id"]


def test_create_unauthorized(api_client):
    """Ensure unauthorized requests are rejected."""
    res = api_client.post(_url_create(), data={})
    assert res.status_code == 401


def test_create_success(api_client):
    """Create progress returns 201 with body."""
    user, video = make_user(), make_video()
    res = api_client.post(
        _url_create(), {"video_id": video.id, "last_position": 33.3},
        **_auth_headers(user),
    )
    assert res.status_code == 201
    assert res.json()["video_id"] == video.id


def test_create_bad_request_missing(api_client):
    """Missing last_position yields 400."""
    user = make_user()
    res = api_client.post(
        _url_create(), {"video_id": 1}, **_auth_headers(user)
    )
    assert res.status_code == 400


def test_create_bad_request_invalid_position(api_client):
    """Negative last_position yields 400."""
    user, video = make_user(), make_video()
    res = api_client.post(
        _url_create(), {"video_id": video.id, "last_position": -1},
        **_auth_headers(user),
    )
    assert res.status_code == 400


def test_create_video_not_found(api_client):
    """Unknown video returns 404."""
    user = make_user()
    res = api_client.post(
        _url_create(), {"video_id": 999999, "last_position": 3},
        **_auth_headers(user),
    )
    assert res.status_code == 404


def test_create_sets_relative_position(api_client):
    """Relative position is computed as percent with 2 decimals."""
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


def test_patch_updates_relative_position(api_client):
    """PATCH updates last_position and recalculates percent."""
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
