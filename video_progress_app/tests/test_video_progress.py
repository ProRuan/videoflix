import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from video_app.models import Video

from video_progress_app.models import VideoProgress

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email='test@example.com', password='pass')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def make_video(db):
    return Video.objects.create(title='Test Vid', description='desc', genre='G')


@pytest.fixture
def make_progress(db, user, make_video):
    def _make(count=1, **fields):
        objs = []
        for i in range(count):
            data = {
                'user': user,
                'video': make_video,
                'last_position': fields.get('last_position', 0),
            }
            data.update(fields)
            objs.append(VideoProgress.objects.create(**data))
        return objs
    return _make


@pytest.mark.django_db
class TestVideoProgressListCreate:
    url = reverse('video-progress-list')

    def test_get_unauthenticated(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_empty_list(self, auth_client):
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # support paginated or flat list
        if isinstance(data, dict):
            assert data.get('count', 0) == 0
            assert data.get('results', []) == []
        else:
            assert data == []

    def test_get_only_owned(self, auth_client, make_progress, user):
        vp = make_progress(count=1)[0]
        # create progress for another user
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
        data = resp.json()
        # handle dict (paginated) or list
        if isinstance(data, dict):
            items = data.get('results', [])
        else:
            items = data

        ids = [item['id'] for item in items]
        # newest (vp2) should appear first
        assert ids == [vp2.id, vp1.id]

    # def test_get_ordering_newest_first(self, auth_client, make_progress):
    #     old, new = make_progress(count=2)
    #     resp = auth_client.get(self.url)
    #     items = resp.json().get('results', resp.json())
    #     ids = [item['id'] for item in items]
    #     assert ids == [new.id, old.id]

    def test_post_unauthenticated(self, api_client, make_video):
        resp = api_client.post(
            self.url, {'video': make_video.id, 'last_position': 10})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_bad_request_missing_fields(self, auth_client):
        resp = auth_client.post(self.url, {}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_bad_request_invalid_position(self, auth_client, make_video):
        resp = auth_client.post(
            self.url, {'video': make_video.id, 'last_position': -1}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_not_found_video(self, auth_client):
        # non-existent video id
        resp = auth_client.post(
            self.url, {'video': 999, 'last_position': 5}, format='json')
        # serializer ValidationError triggers 400
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND)

    def test_post_success(self, auth_client, make_video):
        payload = {'video': make_video.id, 'last_position': 25}
        resp = auth_client.post(self.url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data['video'] == make_video.id
        assert data['last_position'] == 25
        assert 'id' in data
        assert 'updated_at' in data
