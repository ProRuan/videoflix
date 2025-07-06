# Third-party suppliers
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# Local imports
from video_app.models import Video
from video_progress_app.models import VideoProgress

User = get_user_model()


def create_video_progresses(user, video, count=1, **fields):
    """
    Create one or more VideoProgress instances.
    """
    objs = []
    for i in range(count):
        data = {
            'user': user,
            'video': video,
            'last_position': fields.get('last_position', 0),
        }
        data.update(fields)
        objs.append(VideoProgress.objects.create(**data))
    return objs


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
        email='user1@example.com',
        password='pass'
    )


@pytest.fixture
def other_user(db):
    """
    Create another test user.
    """
    return User.objects.create_user(
        email='user2@example.com',
        password='pass'
    )


@pytest.fixture
def auth_client(api_client, user):
    """
    Return an API client authenticated as user.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def make_video(db):
    """
    Create a test video.
    """
    return Video.objects.create(
        title='Vid', description='desc',
        genre='G', duration=100
    )


@pytest.fixture
def make_progress(user, make_video):
    """
    Create a test video progress.
    """
    return lambda count=1, **fields: create_video_progresses(
        user=user, video=make_video, count=count, **fields
    )[0]


@pytest.mark.django_db
class TestVideoProgressDetail:
    """
    Tests for GET/PATCH/DELETE /api/video-progress/{id}/.
    """

    def test_get_unauthenticated(self, api_client):
        """
        Ensure an unauthenticated user can not get video progress
        (status code 401).
        """
        url = reverse('video-progress-detail', args=[1])
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_not_found(self, auth_client):
        """
        Ensure an authenticated user gets status code 404, if the video does
        not exist.
        """
        url = reverse('video-progress-detail', args=[999])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_get_forbidden(
            self, auth_client,
            other_user,
            make_progress,
            make_video
    ):
        """
        Ensure an authenticated user can not get the video progress of another
        user (status code 403).
        """
        vp = VideoProgress.objects.create(
            user=other_user,
            video=make_video,
            last_position=10
        )
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_get_success(self, auth_client, make_progress, make_video):
        """
        Ensure an authenticated user can get his video progress
        (status code 200).
        """
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
        assert data['id'] == vp.id
        assert data['last_position'] == expected['last_position']
        assert data['video'] == expected['video']

    def test_patch_unauthenticated(self, api_client, make_progress):
        """
        Ensure an unauthenticated user can not update a video progress
        (status code 401).
        """
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = api_client.patch(url, {'last_position': 30}, format='json')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_not_found(self, auth_client):
        """
        Ensure a user gets status code 404, if the video does not exist.
        """
        url = reverse('video-progress-detail', args=[999])
        resp = auth_client.patch(url, {'last_position': 30}, format='json')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_forbidden(self, auth_client, other_user, make_video):
        """
        Ensure an authenticated user can not update the video progress of
        another user (status code 403).
        """
        vp = VideoProgress.objects.create(
            user=other_user,
            video=make_video,
            last_position=5
        )
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(url, {'last_position': 50}, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_bad_request_invalid_position(
            self,
            auth_client,
            make_progress
    ):
        """
        Ensure an authenticated user can not update his video progress with an
        invalid playback time (status code 400).
        """
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(url, {'last_position': -5}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_bad_request_exceeds_duration(
            self,
            auth_client,
            make_progress,
            make_video
    ):
        """
        Ensure an authenticated user can not update his video progress, if the
        playback time exceeds the video duration (status code 400).
        """
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(
            url,
            {'last_position': make_video.duration + 1},
            format='json'
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_success(self, auth_client, make_progress):
        """
        Ensure an authenticated user can update his video progress
        (status code 200).
        """
        vp = make_progress(last_position=10)
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.patch(url, {'last_position': 60}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data['last_position'] == 60
        vp.refresh_from_db()
        assert vp.last_position == 60

    def test_delete_unauthenticated(self, api_client, make_progress):
        """
        Ensure an unauthenticated user can not delete a video progress
        (status code 401).
        """
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_not_found(self, auth_client):
        """
        Ensure an authenticated user gets status code 404, if the video does
        not exist.
        """
        url = reverse('video-progress-detail', args=[999])
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_forbidden(self, auth_client, other_user, make_video):
        """
        Ensure an authenticated user can not delete the video progress of
        another user (status code 403).
        """
        vp = VideoProgress.objects.create(
            user=other_user,
            video=make_video,
            last_position=5
        )
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_success(self, auth_client, make_progress):
        """
        Ensure an authenticated user can delete his video progress
        (status code 204).
        """
        vp = make_progress()
        url = reverse('video-progress-detail', args=[vp.id])
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        with pytest.raises(VideoProgress.DoesNotExist):
            VideoProgress.objects.get(id=vp.id)
