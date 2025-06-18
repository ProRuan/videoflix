import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from video_offer_app.models import Video


def VIDEO_DETAIL_URL(vid): return f'/api/videos/{vid}/'


@pytest.mark.django_db
def test_get_video_success_returns_200(client):
    """Ensure GET returns 200 and video object."""
    video = Video.objects.create(title='Test', description='Test Desc')
    response = client.get(VIDEO_DETAIL_URL(video.id))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == video.id
    assert data["title"] == video.title


@pytest.mark.django_db
def test_get_video_not_found_returns_404(client):
    """Ensure GET on non-existent ID returns 404."""
    response = client.get(VIDEO_DETAIL_URL(999))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_video_success_returns_200(client):
    """Ensure PATCH updates fields and returns updated video (200)."""
    admin = User.objects.create_user(
        username='admin', password='pw', is_staff=True)
    client.login(username='admin', password='pw')

    video = Video.objects.create(title='Original', description='Desc')

    response = client.patch(
        VIDEO_DETAIL_URL(video.id),
        data={'title': 'Updated'},
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    video.refresh_from_db()
    assert video.title == 'Updated'


@pytest.mark.django_db
def test_patch_video_unauthenticated_returns_401(client):
    """Ensure PATCH without login returns 401."""
    video = Video.objects.create(title='T', description='D')
    response = client.patch(
        VIDEO_DETAIL_URL(video.id),
        data={'title': 'New'},
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_video_invalid_data_returns_400(client):
    """Ensure PATCH with invalid data returns 400."""
    admin = User.objects.create_user(
        username='admin', password='pw', is_staff=True)
    client.login(username='admin', password='pw')

    video = Video.objects.create(title='Valid', description='Valid desc')

    response = client.patch(
        VIDEO_DETAIL_URL(video.id),
        data={'title': ''},  # Invalid title
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_video_success_returns_204(client):
    """Ensure DELETE as admin deletes the video (204)."""
    admin = User.objects.create_user(
        username='admin', password='pw', is_staff=True)
    client.login(username='admin', password='pw')

    video = Video.objects.create(title='To Delete', description='Desc')
    response = client.delete(VIDEO_DETAIL_URL(video.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Video.objects.filter(id=video.id).exists()


@pytest.mark.django_db
def test_delete_video_unauthenticated_returns_401(client):
    """Ensure DELETE without login returns 401."""
    video = Video.objects.create(title='T', description='D')
    response = client.delete(VIDEO_DETAIL_URL(video.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_video_non_admin_returns_403(client):
    """Ensure DELETE as non-staff returns 403."""
    user = User.objects.create_user(username='user', password='pw')
    client.login(username='user', password='pw')

    video = Video.objects.create(title='Protected', description='D')
    response = client.delete(VIDEO_DETAIL_URL(video.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_video_not_found_returns_404(client):
    """Ensure DELETE on non-existent ID returns 404."""
    admin = User.objects.create_user(
        username='admin', password='pw', is_staff=True)
    client.login(username='admin', password='pw')

    response = client.delete(VIDEO_DETAIL_URL(999))
    assert response.status_code == status.HTTP_404_NOT_FOUND
