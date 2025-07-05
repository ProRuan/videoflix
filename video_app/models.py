# Standard library
from datetime import date

# Third-party suppliers
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Local imports
from .storage_backends import OverwriteStorage

User = get_user_model()

overwrite_storage = OverwriteStorage()


class Video(models.Model):
    """
    Represents a video.
    """
    title = models.CharField(max_length=80, default='')
    genre = models.CharField(max_length=80, default='')
    description = models.CharField(max_length=500, default='')
    video_file = models.FileField(
        upload_to='videos/original/', storage=overwrite_storage,
        blank=True, null=True,
    )
    hls_playlist = models.FileField(
        upload_to='videos/hls/', storage=overwrite_storage,
        blank=True, null=True,
    )
    preview_clip = models.FileField(
        upload_to='videos/preview/', storage=overwrite_storage,
        blank=True, null=True,
    )
    thumbnail_image = models.ImageField(
        upload_to='videos/thumbs/', storage=overwrite_storage,
        blank=True, null=True,
    )
    sprite_sheet = models.FileField(
        upload_to='videos/sprites/', storage=overwrite_storage,
        blank=True, null=True,
    )
    duration = models.IntegerField(
        blank=True, null=True,
        help_text='Duration in seconds'
    )
    available_resolutions = ArrayField(
        models.CharField(max_length=10), default=list,
        blank=True,
    )
    created_at = models.DateField(default=date.today)

    def __str__(self):
        """
        Get a string representing a video by title.
        """
        return self.title
