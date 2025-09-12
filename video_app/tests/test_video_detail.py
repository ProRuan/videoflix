# Standard libraries

# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APIClient

# Local imports
from video_app.models import Video
from video_app.tests.utils.factories import make_user, make_token, make_video


@pytest.mark.django_db
def test_video_detail_success():
    """
    Ensure authenticated user can get a single video.
    """
    user = make_user()
    token = make_token(user)
    video = make_video("A", "Drama")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    url = reverse("video_app:video-detail", args=[video.id])
    res = client.get(url)
    assert res.status_code == 200
    assert res.data["id"] == video.id


@pytest.mark.django_db
def test_video_detail_unauthorized():
    """
    Ensure request without token is unauthorized.
    """
    video = make_video()
    client = APIClient()
    url = reverse("video_app:video-detail", args=[video.id])
    res = client.get(url)
    assert res.status_code == 401


@pytest.mark.django_db
def test_video_detail_not_found():
    """
    Ensure not found for non-existing video id.
    """
    user = make_user()
    token = make_token(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    url = reverse("video_app:video-detail", args=[999999])
    res = client.get(url)
    assert res.status_code == 404


@pytest.mark.django_db
def test_video_detail_absolute_urls():
    """
    Ensure media URLs are absolute in the API response.
    """
    User = get_user_model()
    user = User.objects.create_user(email="u@mail.com", password="pass1234")
    _, token = AuthToken.objects.create(user)

    v = Video.objects.create(
        title="Clip", genre="Action",
        hls_playlist="videos/hls/v1/master.m3u8",
        preview="videos/previews/v1.mp4",
        thumbnail="videos/thumbs/v1.jpg",
        quality_levels=[
            {"label": "1080p", "source": "/media/videos/hls/v1/v0/index.m3u8"}
        ],
    )

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    url = reverse("video_app:video-detail", args=[v.id])
    res = client.get(url)

    assert res.status_code == 200
    assert res.data["hls_playlist"].startswith("http://testserver/")
    assert res.data["preview"].startswith("http://testserver/")
    assert res.data["thumbnail"].startswith("http://testserver/")
    q = res.data["quality_levels"][0]["source"]
    assert q.startswith("http://testserver/")
