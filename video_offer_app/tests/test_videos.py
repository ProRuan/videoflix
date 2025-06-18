import io
import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from video_offer_app.models import Video

VIDEO_URL = '/api/videos/'


@pytest.mark.django_db
def test_get_videos_success_returns_200(client):
    """Ensure GET returns 200 and list of videos."""
    Video.objects.create(title='Video 1', description='Desc 1')

    response = client.get(VIDEO_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


@pytest.mark.django_db
def test_get_videos_bad_request_returns_400(client):
    """Ensure GET with invalid params returns 400."""
    response = client.get(VIDEO_URL, data={'invalid': 'param'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_post_video_requires_authentication(client):
    """Ensure unauthenticated POST returns 401."""
    file = SimpleUploadedFile("test.mp4", b"content", content_type="video/mp4")
    response = client.post(
        VIDEO_URL,
        data={'title': 'T', 'description': 'D', 'video_file': file},
        format='multipart'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_video_requires_admin(client):
    """Ensure non-staff user POST returns 403."""
    user = User.objects.create_user(username='user', password='pw')
    client.login(username='user', password='pw')

    file = SimpleUploadedFile("test.mp4", b"content", content_type="video/mp4")
    response = client.post(
        VIDEO_URL,
        data={'title': 'T', 'description': 'D', 'video_file': file},
        format='multipart'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_post_video_bad_data_returns_400(client):
    """Ensure POST with missing fields returns 400."""
    admin = User.objects.create_user(
        username='admin', password='pw', is_staff=True)
    client.login(username='admin', password='pw')

    # Missing title
    file = SimpleUploadedFile("test.mp4", b"content", content_type="video/mp4")
    response = client.post(
        VIDEO_URL,
        data={'description': 'Only desc', 'video_file': file},
        format='multipart'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert 'title' in data


@pytest.mark.django_db
def test_post_video_success_returns_201(client):
    """Ensure staff user can POST and create video (201)."""
    admin = User.objects.create_user(
        username='admin', password='pw', is_staff=True)
    client.login(username='admin', password='pw')

    file = SimpleUploadedFile(
        "test.mp4", b"video content", content_type="video/mp4")
    response = client.post(
        VIDEO_URL,
        data={'title': 'My Video', 'description': 'Desc', 'video_file': file},
        format='multipart'
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['title'] == 'My Video'
    assert data['description'] == 'Desc'

    video = Video.objects.get(id=data['id'])
    assert video.title == 'My Video'
    assert video.description == 'Desc'
