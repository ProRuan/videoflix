# Standard libraries
from datetime import date, timedelta

# Third-party supplier
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# Local imports
from video_app.models import Video

User = get_user_model()


def create_videos(count=1, **fields):
    """
    Create multiple Video instances.
    """
    videos = []
    for i in range(count):
        base_date = date.today() + timedelta(days=i)
        data = {
            'title': f'Video {i+1}',
            'description': f'Description {i+1}',
            'genre': fields.get('genre', ''),
            'created_at': fields.get('created_at', base_date),
        }
        data.update(fields)
        videos.append(Video.objects.create(**data))
    return videos


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
        password='password'
    )


@pytest.fixture
def auth_client(api_client, user):
    """
    Return an API client authenticated as user.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def make_videos(db):
    """
    Create a video list.
    """
    return create_videos


@pytest.mark.django_db
class TestVideoList:
    """
    Tests for GET /api/videos/.
    """
    @pytest.fixture(autouse=True)
    def setup_url(self):
        """
        Set up endpoint url.
        """
        self.url = reverse('video-list')

    def test_empty_list(self, auth_client):
        """
        Ensure getting an empty list when no videos exist.
        """
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_sorted_by_date(self, auth_client, make_videos):
        """
        Ensure getting a video list sorted by created_at.
        Newest videos are listed first.
        """
        today = date.today()
        old, mid, new = (
            *make_videos(count=1, created_at=today - timedelta(days=2)),
            *make_videos(count=1, created_at=today - timedelta(days=1)),
            *make_videos(count=1, created_at=today)
        )
        response = auth_client.get(self.url)
        ids = [v['id'] for v in response.json()]
        assert ids == [new.id, mid.id, old.id]

    def test_filter_genre(self, auth_client, make_videos):
        """
        Ensure videos are filtered by genre and case-insensitively.
        """
        make_videos(count=1, genre='Comedy')
        action_videos = make_videos(count=2, genre='Action')
        response = auth_client.get(self.url, {'genre': 'action'})
        ids = {v['id'] for v in response.json()}
        assert ids == {vid.id for vid in action_videos}

    def test_filter_and_sort(self, auth_client, make_videos):
        """
        Ensure filtering and default sorting work together.
        """
        today = date.today()
        make_videos(
            count=1, genre='Action',
            created_at=today - timedelta(days=1)
        )
        latest = make_videos(count=1, genre='Action', created_at=today)[0]
        response = auth_client.get(self.url, {'genre': 'Action'})
        assert response.json()[0]['id'] == latest.id
