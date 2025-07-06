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
    Create one or more VideoProgress instances for testing.
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
        email='test@example.com',
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
    Create a video for testing.
    """
    return Video.objects.create(
        title='Test Vid',
        description='desc',
        genre='G'
    )


@pytest.fixture
def make_progress(db, user, make_video):
    """
    Create video progress list.
    """
    return lambda count=1, **fields: create_video_progresses(
        user=user, video=make_video,
        count=count, **fields
    )


@pytest.mark.django_db
class TestVideoProgressListCreate:
    """
    Tests for GET/POST /api/video-progress/.
    """
    url = reverse('video-progress-list')

    def test_get_unauthenticated(self, api_client):
        """
        Ensure unauthenticated user can not get video progress list
        (status code 401).
        """
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_empty_list(self, auth_client):
        """
        Ensure user can get an empty list (status code 200).
        """
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data == []

    def test_get_only_owned(self, auth_client, make_progress, user):
        """
        Ensure authenticated user can only get list of his own video progress
        (status code 200).
        """
        vp = make_progress(count=1)[0]
        other = User.objects.create_user(
            email='other@example.com', password='pass')
        VideoProgress.objects.create(
            user=other, video=vp.video, last_position=5)
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        items = data['results'] if isinstance(data, dict) else data
        assert len(items) == 1
        assert items[0]['id'] == vp.id

    def test_get_ordering_newest_first(self, auth_client, user):
        """
        Ensure video progress list shows newest videos first (status code 200).
        """
        video1 = Video.objects.create(
            title='Video A', description='Desc A', genre='G')
        video2 = Video.objects.create(
            title='Video B', description='Desc B', genre='G')
        vp1 = VideoProgress.objects.create(
            user=user, video=video1, last_position=5)
        vp2 = VideoProgress.objects.create(
            user=user, video=video2, last_position=15)
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        items = resp.json()
        ids = [item['id'] for item in items]
        assert ids == [vp2.id, vp1.id]

    def test_post_unauthenticated(self, api_client, make_video):
        """
        Ensure an unauthenticated user can not create a video progress
        (status code 400).
        """
        resp = api_client.post(
            self.url, {'video': make_video.id, 'last_position': 10})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_bad_request_missing_fields(self, auth_client):
        """
        Ensure authenticated user can not create a video progress with incomplete
        request data (status code 400).
        """
        resp = auth_client.post(self.url, {}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_bad_request_invalid_position(self, auth_client, make_video):
        """
        Ensure an authenticated user can not create a video progress with an
        invalid playback time (status code 400).
        """
        resp = auth_client.post(
            self.url, {'video': make_video.id, 'last_position': -1}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_not_found_video(self, auth_client):
        """
        Ensure an authenticated user can not create a video progress, if the
        video is not existent (status code 404).
        """
        resp = auth_client.post(
            self.url, {'video': 999, 'last_position': 5}, format='json')
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND)

    def test_post_success(self, auth_client, make_video):
        """
        Ensure an authenticated user can create a video progress
        (status code 201).
        """
        payload = {'video': make_video.id, 'last_position': 25}
        resp = auth_client.post(self.url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data['video'] == make_video.id
        assert data['last_position'] == 25
        assert 'id' in data
        assert 'updated_at' in data
