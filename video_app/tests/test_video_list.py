import pytest
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

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
                'created_at': fields.get('created_at', date.today() + timedelta(days=i)),
            }
            for k, v in fields.items():
                if k not in data:
                    data[k] = v
            objs.append(Video.objects.create(**data))
        return objs
    return _make


@pytest.mark.django_db
class TestVideoList:
    url = reverse('video-list')

    def test_list_empty(self, auth_client):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['count'] == 0
        assert data['results'] == []

    def test_list_sorted(self, auth_client, make_videos):
        today = date.today()
        v1 = make_videos(count=1, created_at=today - timedelta(days=2))[0]
        v2 = make_videos(count=1, created_at=today - timedelta(days=1))[0]
        v3 = make_videos(count=1, created_at=today)[0]

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()['results']
        assert [item['id'] for item in data] == [v3.id, v2.id, v1.id]

    def test_filter_by_genre(self, auth_client, make_videos):
        make_videos(count=1, genre='Comedy')
        actions = make_videos(count=2, genre='Action')

        response = auth_client.get(self.url, {'genre': 'Action'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()['results']
        ids = {item['id'] for item in data}
        assert ids == {v.id for v in actions}

    def test_combined(self, auth_client, make_videos):
        today = date.today()
        make_videos(count=1, genre='Action',
                    created_at=today - timedelta(days=1))
        latest = make_videos(count=1, genre='Action', created_at=today)[0]
        make_videos(count=1, genre='Comedy', created_at=today)

        response = auth_client.get(self.url, {'genre': 'Action'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()['results']
        assert data[0]['id'] == latest.id


@pytest.mark.django_db
def test_pagination(auth_client, make_videos):
    make_videos(count=6)
    response = auth_client.get(reverse('video-list'))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'results' in data and len(data['results']) == 4
    assert data['count'] == 6
    assert data['next']
    assert data['previous'] is None
