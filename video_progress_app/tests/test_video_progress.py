# Third-party suppliers
import pytest
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from .utils.factories import make_user, make_video


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def _auth_headers(user):
    _, token = AuthToken.objects.create(user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def test_create_unauthorized(api_client, db):
    url = reverse("video_progress_app:video-progress-create")
    res = api_client.post(url, data={})
    assert res.status_code == 401


def test_create_success(api_client, db):
    user = make_user()
    video = make_video()
    headers = _auth_headers(user)
    body = dict(video_id=video.id, last_position=33.3)
    url = reverse("video_progress_app:video-progress-create")
    res = api_client.post(url, data=body, **headers)
    assert res.status_code == 201
    assert res.json()["video_id"] == video.id


def test_create_bad_request_missing(api_client, db):
    user = make_user()
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-create")
    res = api_client.post(url, data={"video_id": 1}, **headers)
    assert res.status_code == 400


def test_create_bad_request_invalid_position(api_client, db):
    user = make_user()
    video = make_video()
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-create")
    res = api_client.post(
        url, data={"video_id": video.id, "last_position": -1}, **headers
    )
    assert res.status_code == 400


def test_create_video_not_found(api_client, db):
    user = make_user()
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-create")
    res = api_client.post(
        url, data={"video_id": 999999, "last_position": 3}, **headers
    )
    assert res.status_code == 404
