# tests/test_video_detail.py
# Standard libraries
from datetime import date, timedelta
import os

# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# Local imports
from video_app.models import Video
from django.conf import settings

User = get_user_model()


def create_videos(count=1, **fields):
    """
    Create multiple Video instances.
    """
    vids = []
    for i in range(count):
        base_date = date.today() + timedelta(days=i)
        data = {
            'title': f'Video {i+1}',
            'description': f'Description {i+1}',
            'genre': fields.get('genre', ''),
            'created_at': fields.get('created_at', base_date),
        }
        data.update(fields)
        vids.append(Video.objects.create(**data))
    return vids


def assert_valid_video_response(data, video):
    """
    Assert all expected fields and values exist in video response.
    """
    expected = [
        'id', 'created_at', 'genre', 'title', 'description',
        'duration', 'available_resolutions',
        'thumbnail_image', 'preview_clip', 'hls_playlist',
        'video_file'
    ]
    for field in expected:
        assert field in data
    assert data['id'] == video.id
    assert data['title'] == video.title
    assert data['genre'] == video.genre

    # additional checks for the new resolution mapping shape
    ar = data['available_resolutions']
    assert isinstance(ar, dict)
    # each value should look like a playlist URL path under videos/hls and end with index.m3u8
    for name, url in ar.items():
        assert '/videos/hls/' in url
        assert url.endswith('/index.m3u8')


@pytest.fixture
def api_client():
    """
    Return an unauthenticated API client.
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Create a test user.
    """
    return User.objects.create_user(
        email='test@example.com', password='password'
    )


@pytest.fixture
def auth_client(api_client, user):
    """
    Return API client authenticated as user.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestVideoDetail:
    """
    Tests for GET /api/videos/{id}/.
    """

    def test_unauthenticated(self, api_client):
        """
        Ensure unauthenticated user can not get video (status code 401).
        """
        url = reverse('video-detail', args=[1])
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_not_found(self, auth_client):
        """
        Ensure non-existent video ID returns status code 404.
        """
        url = reverse('video-detail', args=[999])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_success_returns_all_fields(self, auth_client):
        """
        Ensure getting a valid video with all model fields including
        available_resolutions mapping built from hls_playlist.
        """
        vid = create_videos(count=1)[0]

        # simulate HLS generation: set hls_playlist name and available_resolutions list
        # choose a base name that will be used to build URLs
        base = 'mighty_magic'
        # set the stored file names (these do not need to point to real files for the test)
        vid.hls_playlist.name = os.path.join('videos', 'hls', f"{base}.m3u8")
        vid.available_resolutions = ['1080p', '720p']
        vid.save(update_fields=['hls_playlist', 'available_resolutions'])

        url = reverse('video-detail', args=[vid.id])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert_valid_video_response(resp.json(), vid)
