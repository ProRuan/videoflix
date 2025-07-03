import pytest
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from video_app.models import Video


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(email='test@example.com', password='password')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def make_videos(db):
    def _make(count=1, **fields):
        objs = []
        for i in range(count):
            data = {
                'title': f'Video {i+1}',
                'description': f'Description {i+1}',
                'genre': fields.get('genre', ''),
                'created_at': fields.get('created_at', date.today()),
            }
            data.update({k: v for k, v in fields.items() if k not in data})
            objs.append(Video.objects.create(**data))
        return objs
    return _make


@pytest.mark.django_db
class TestVideoDetail:
    """
    Test GET /api/videos/{video_id}/
    """

    def test_unauthenticated(self, api_client):
        url = reverse('video-detail', args=[1])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_not_found(self, auth_client):
        url = reverse('video-detail', args=[999])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success(self, auth_client, make_videos):
        video = make_videos(count=1)[0]
        url = reverse('video-detail', args=[video.id])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Check all expected fields
        expected_fields = [
            'id', 'created_at', 'genre', 'title', 'description',
            'duration', 'available_resolutions',
            'thumbnail_image', 'preview_clip', 'hls_playlist', 'video_file'
        ]
        for field in expected_fields:
            assert field in data
        assert data['id'] == video.id
        assert data['title'] == video.title
        assert data['description'] == video.description
        assert data['genre'] == video.genre
