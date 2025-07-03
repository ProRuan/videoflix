import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from datetime import timedelta

from video_app.models import Video
from video_progress_app.models import VideoProgress

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email='user1@example.com', password='pass')


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email='user2@example.com', password='pass')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def make_video(db):
    return Video.objects.create(title='Vid', description='desc', genre='G', duration=100)


@pytest.fixture
def make_progress(db, user, make_video):
    def _make(video=None, last_position=0):
        return VideoProgress.objects.create(
            user=user,
            video=video or make_video,
            last_position=last_position
        )
    return _make


@pytest.mark.django_db
class TestVideoProgressDetail:
    def test_get_unauthenticated(self, api_client):
        url = reverse('video-progress-detail', args=[1])
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_not_found(self, auth_client):
        url = reverse('video-progress-detail', args=[999])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_get_forbidden(self, auth_client, other_user, make_progress, make_video):
        # Create a progress for other_user
        vp = VideoProgress.objects.create(
            user=other_user, video=make_video, last_position=10)
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_get_success(self, auth_client, make_progress, make_video):
        vp = make_progress(last_position=20)
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        expected = {
            'user': auth_client.handler._force_user.id,
            'video': make_video.id,
            'last_position': 20
        }
        # check presence of updated_at and id
        assert data['id'] == vp.id
        assert data['last_position'] == expected['last_position']
        assert data['video'] == expected['video']
        assert 'updated_at' in data

    def test_patch_unauthenticated(self, api_client, make_progress):
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = api_client.patch(url, {'last_position': 30}, format='json')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_not_found(self, auth_client):
        url = reverse('video-progress-detail', args=[999])
        resp = auth_client.patch(url, {'last_position': 30}, format='json')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_forbidden(self, auth_client, other_user, make_video):
        vp = VideoProgress.objects.create(
            user=other_user, video=make_video, last_position=5)
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(url, {'last_position': 50}, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_bad_request_invalid_position(self, auth_client, make_progress):
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(url, {'last_position': -5}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_bad_request_exceeds_duration(self, auth_client, make_progress, make_video):
        vp = make_progress(video=make_video)
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(
            url, {'last_position': make_video.duration + 1}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_success(self, auth_client, make_progress):
        vp = make_progress(last_position=10)
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(url, {'last_position': 60}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data['last_position'] == 60
        # verify DB updated
        vp.refresh_from_db()
        assert vp.last_position == 60

    def test_delete_unauthenticated(self, api_client, make_progress):
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_not_found(self, auth_client):
        url = reverse('video-progress-detail', args=[999])
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_forbidden(self, auth_client, other_user, make_video):
        vp = VideoProgress.objects.create(
            user=other_user, video=make_video, last_position=5)
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_success(self, auth_client, make_progress):
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        with pytest.raises(VideoProgress.DoesNotExist):
            VideoProgress.objects.get(id=vp.id)
