# Third-party suppliers
import pytest
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from .utils.factories import make_user, make_video, make_progress


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def _auth_headers(user):
    _, token = AuthToken.objects.create(user)
    return {"HTTP_AUTHORIZATION": f"Token {token}"}


def test_detail_success_patch(api_client, db):
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 1.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={"last_position": 9.5}, **headers)
    assert res.status_code == 200
    assert res.json()["last_position"] == 9.5


def test_detail_bad_request_patch_missing(api_client, db):
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 1.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={}, **headers)
    assert res.status_code == 400


def test_detail_bad_request_patch_invalid(api_client, db):
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 1.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={"last_position": -2}, **headers)
    assert res.status_code == 400


def test_detail_forbidden_patch(api_client, db):
    a = make_user("a@mail.com")
    b = make_user("b@mail.com")
    video = make_video()
    prog = make_progress(a, video, 3.0)
    headers = _auth_headers(b)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.patch(url, data={"last_position": 8}, **headers)
    assert res.status_code == 403


def test_detail_not_found_patch(api_client, db):
    user = make_user()
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": 999999})
    res = api_client.patch(url, data={"last_position": 1}, **headers)
    assert res.status_code == 404


def test_detail_success_delete(api_client, db):
    user = make_user()
    video = make_video()
    prog = make_progress(user, video, 2.0)
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.delete(url, **headers)
    assert res.status_code == 204


def test_detail_forbidden_delete(api_client, db):
    a = make_user("a@mail.com")
    b = make_user("b@mail.com")
    video = make_video()
    prog = make_progress(a, video, 2.0)
    headers = _auth_headers(b)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": prog.id})
    res = api_client.delete(url, **headers)
    assert res.status_code == 403


def test_detail_not_found_delete(api_client, db):
    user = make_user()
    headers = _auth_headers(user)
    url = reverse("video_progress_app:video-progress-detail",
                  kwargs={"pk": 999999})
    res = api_client.delete(url, **headers)
    assert res.status_code == 404
