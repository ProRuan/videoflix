# tests/test_video_list.py
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


def _flatten_response(resp_json):
    """
    Flatten grouped response into a list of videos preserving order.
    """
    return [v for group in resp_json for v in group.get('videos', [])]


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
        Ensure videos are returned grouped by genre and that, within a
        genre, videos are sorted by created_at (newest first).
        """
        today = date.today()
        old = make_videos(count=1, created_at=today - timedelta(days=2))[0]
        mid = make_videos(count=1, created_at=today - timedelta(days=1))[0]
        new = make_videos(count=1, created_at=today)[0]

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        flattened = _flatten_response(response.json())
        ids = [v['id'] for v in flattened]
        assert ids == [new.id, mid.id, old.id]

    def test_grouped_by_genre_and_sorted(self, auth_client, make_videos):
        """
        Ensure response is grouped by genre (alphabetical) and videos inside
        each genre are sorted by created_at (newest first) and title (secondary).
        """
        today = date.today()
        # Action videos: two with different dates
        a1 = make_videos(count=1, genre='Action',
                         created_at=today - timedelta(days=1))[0]
        a2 = make_videos(count=1, genre='Action', created_at=today)[0]
        # Comedy single
        c1 = make_videos(count=1, genre='Comedy',
                         created_at=today - timedelta(days=2))[0]

        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        # genres should be alphabetically ordered: Action, Comedy
        genres = [g['genre'] for g in data]
        assert genres == ['Action', 'Comedy']

        # videos in Action should be newest first
        action_videos = next(g for g in data if g['genre'] == 'Action')[
            'videos']
        assert action_videos[0]['id'] == a2.id
        assert action_videos[1]['id'] == a1.id

        # Comedy has the single video
        comedy_videos = next(g for g in data if g['genre'] == 'Comedy')[
            'videos']
        assert comedy_videos[0]['id'] == c1.id
