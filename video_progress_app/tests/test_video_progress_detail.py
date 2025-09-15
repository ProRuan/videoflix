# Third-party suppliers
import pytest
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from .utils.factories import make_user, make_video, make_progress


@pytest.fixture
def api_client() -> APIClient:
    """Get APIClient."""
    return APIClient()


def _auth_headers(user):
    """Get auth headers."""
    _, token = AuthToken.objects.create(user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def test_video_progress_patch_success(api_client, db):
    """Test for successful video progress update."""
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 1.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={"last_position": 9.5}, **headers)
    assert res.status_code == 200
    assert res.json()["last_position"] == 9.5


def test_video_progress_patch_missing_data(api_client, db):
    """Test for video progress update with missing data."""
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 1.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={}, **headers)
    assert res.status_code == 400


def test_video_progress_patch_invalid_data(api_client, db):
    """Test for video progress update with invalid data."""
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 1.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={"last_position": -2}, **headers)
    assert res.status_code == 400


def test_video_progress_patch_no_permission(api_client, db):
    """Test for video progress update with non-owner."""
    a = make_user("a@mail.com")
    b = make_user("b@mail.com")
    video = make_video()
    prog = make_progress(a, video, 3.0)
    headers = _auth_headers(b)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={"last_position": 8}, **headers)
    assert res.status_code == 403


def test_video_progress_patch_not_found(api_client, db):
    """Test for video progress update with non-existing video progress."""
    user = make_user()
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": 999999})
    res = api_client.patch(url, data={"last_position": 1}, **headers)
    assert res.status_code == 404


def test_video_progress_delete_success(api_client, db):
    """Test for successful video progress deletion."""
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 2.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.delete(url, **headers)
    assert res.status_code == 204


def test_video_progress_delete_no_permission(api_client, db):
    """Test for video progress deletion with non-owner."""
    a = make_user("a@mail.com")
    b = make_user("b@mail.com")
    video = make_video()
    prog = make_progress(a, video, 2.0)
    headers = _auth_headers(b)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.delete(url, **headers)
    assert res.status_code == 403


def test_video_progress_delete_not_found(api_client, db):
    """Test for video progress deletion with non-existing video progress."""
    user = make_user()
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": 999999})
    res = api_client.delete(url, **headers)
    assert res.status_code == 404
