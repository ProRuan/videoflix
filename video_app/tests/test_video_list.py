# Standard libraries

# Third-party suppliers
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Local imports
from video_app.tests.utils.factories import (
    make_user, make_token, make_video, set_created_at
)


@pytest.mark.django_db
def test_videos_list_success():
    """
    Ensure authenticated user receives grouped videos with 'New' first.
    """
    user = make_user()
    token = make_token(user)
    v1 = make_video("A", "Drama")
    v2 = make_video("B", "Action")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    url = reverse("video_app:video-list")
    res = client.get(url)
    assert res.status_code == 200
    assert res.data[0]["genre"] == "New on Videoflix"
    genres = [g["genre"] for g in res.data]
    assert "Drama" in genres and "Action" in genres


@pytest.mark.django_db
def test_videos_list_unauthorized():
    """
    Ensure request without token is unauthorized.
    """
    client = APIClient()
    url = reverse("video_app:video-list")
    res = client.get(url)
    assert res.status_code == 401
