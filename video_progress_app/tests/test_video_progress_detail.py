# Third-party suppliers
import pytest
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from .utils.factories import make_user, make_video, make_progress


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    """Get APIClient."""
    return APIClient()


def _auth_headers(user):
    """Get auth headers for specific user."""
    _, token = AuthToken.objects.create(user=user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def _detail_url(pk: int):
    """Get video progress detail URL."""
    return reverse("video_progress_app:video-progress-detail", kwargs={"pk": pk})


def test_video_progress_patch_success(api_client, db):
    """Test for successful video progress update."""
    user, video = make_user(), make_video()
    prog = make_progress(user, video, 1.0)
    res = api_client.patch(_detail_url(prog.id), {"last_position": 9.5},
                           **_auth_headers(user))
    assert res.status_code == 200
    assert res.json()["last_position"] == 9.5


def test_video_progress_patch_missing_data(api_client, db):
    """Test for video progress update with missing data."""
    user, video = make_user(), make_video()
    prog = make_progress(user, video, 1.0)
    res = api_client.patch(_detail_url(prog.id), {}, **_auth_headers(user))
    assert res.status_code == 400


def test_video_progress_patch_invalid_data(api_client, db):
    """Test for video progress update with invalid data."""
    user, video = make_user(), make_video()
    prog = make_progress(user, video, 1.0)
    res = api_client.patch(_detail_url(prog.id), {"last_position": -2},
                           **_auth_headers(user))
    assert res.status_code == 400


def test_video_progress_patch_no_permission(api_client, db):
    """Test for video progress update with non-owner."""
    a, b, video = make_user(
        "a@mail.com"), make_user("b@mail.com"), make_video()
    prog = make_progress(a, video, 3.0)
    res = api_client.patch(_detail_url(prog.id), {"last_position": 8},
                           **_auth_headers(b))
    assert res.status_code == 403


def test_video_progress_patch_not_found(api_client, db):
    """Test for video progress update with non-existing video progress."""
    user = make_user()
    res = api_client.patch(_detail_url(999999), {"last_position": 1},
                           **_auth_headers(user))
    assert res.status_code == 404


def test_video_progress_delete_success(api_client, db):
    """Test for successful video progress deletion."""
    user, video = make_user(), make_video()
    prog = make_progress(user, video, 2.0)
    res = api_client.delete(_detail_url(prog.id), **_auth_headers(user))
    assert res.status_code == 204


def test_video_progress_delete_no_permission(api_client, db):
    """Test for video progress deletion with non-owner."""
    a, b, video = make_user(
        "a@mail.com"), make_user("b@mail.com"), make_video()
    prog = make_progress(a, video, 2.0)
    res = api_client.delete(_detail_url(prog.id), **_auth_headers(b))
    assert res.status_code == 403


def test_video_progress_delete_not_found(api_client, db):
    """Test for video progress deletion with non-existing video progress."""
    user = make_user()
    res = api_client.delete(_detail_url(999999), **_auth_headers(user))
    assert res.status_code == 404
