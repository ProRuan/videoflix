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

    def test_new_group_first_and_sorted(self, auth_client, make_videos):
        """
        The first element must be the "New on Videoflix" group and contain
        recent videos (sorted by created_at desc).
        Other genre groups follow alphabetically and contain their videos
        sorted newest-first then title.
        """
        today = date.today()

        # Action: one yesterday, one today (today is "new")
        a1 = make_videos(count=1, genre='Action',
                         created_at=today - timedelta(days=1))[0]
        a2 = make_videos(count=1, genre='Action', created_at=today)[0]

        # Comedy: old (outside default 14-day "new" window)
        c1 = make_videos(count=1, genre='Comedy',
                         created_at=today - timedelta(days=20))[0]

        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()

        # first group is the New on Videoflix group and contains the newest video(s)
        assert len(data) >= 3  # New + Action + Comedy (at least)
        assert data[0]['genre'] == 'New on Videoflix'
        new_videos = data[0]['videos']
        assert any(v['id'] == a2.id for v in new_videos)
        # newest-first inside the new group
        assert new_videos[0]['id'] == a2.id

        # remaining genres are alphabetical
        rest_genres = [g['genre'] for g in data[1:]]
        assert rest_genres == sorted(rest_genres)

        # Action group should contain both Action videos, newest-first
        action_group = next(g for g in data if g['genre'] == 'Action')
        assert action_group['videos'][0]['id'] == a2.id
        assert action_group['videos'][1]['id'] == a1.id

        # Comedy group has the old video
        comedy_group = next(g for g in data if g['genre'] == 'Comedy')
        assert comedy_group['videos'][0]['id'] == c1.id
