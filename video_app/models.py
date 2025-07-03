from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import date
from .storage_backends import OverwriteStorage
from django.contrib.auth import get_user_model

User = get_user_model()

overwrite_storage = OverwriteStorage()


class Video(models.Model):
    title = models.CharField(max_length=80)
    genre = models.CharField(max_length=80, default='')
    description = models.CharField(max_length=500)
    video_file = models.FileField(
        upload_to='videos/original/', storage=overwrite_storage,
        blank=True, null=True,
        help_text='Upload a video file.'
    )
    hls_playlist = models.FileField(
        upload_to='videos/hls/', storage=overwrite_storage,
        blank=True, null=True,
        help_text='Auto-generated upon file upload.'
    )
    preview_clip = models.FileField(
        upload_to='videos/preview/', storage=overwrite_storage,
        blank=True, null=True,
        help_text='Auto-generated upon file upload.'
    )
    thumbnail_image = models.ImageField(
        upload_to='videos/thumbs/', storage=overwrite_storage,
        blank=True, null=True,
        help_text='Auto-generated upon file upload.'
    )
    sprite_sheet = models.FileField(
        upload_to='videos/sprites/', storage=overwrite_storage,
        blank=True, null=True,
        help_text='Auto-generated upon file upload.'
    )
    duration = models.IntegerField(
        blank=True, null=True,
        help_text='Auto-generated upon file upload.'
    )
    available_resolutions = ArrayField(
        models.CharField(max_length=10), default=list,
        blank=True, help_text='Auto-generated upon file upload.'
    )
    created_at = models.DateField(default=date.today)

    def __str__(self):
        return self.title
