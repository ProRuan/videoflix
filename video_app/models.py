# Standard libraries
from datetime import timedelta

# Third-party suppliers
from django.db import models

# Local imports


class Video(models.Model):
    """
    Stores a single video and its derived assets for HLS playback.
    """
    title = models.CharField(max_length=200, default='')
    genre = models.CharField(max_length=100, default='')
    description = models.TextField(blank=True, default='')
    duration = models.FloatField(default=0.0)  # seconds
    video_file = models.FileField(
        upload_to="videos/originals/", blank=True, null=True)
    hls_playlist = models.FileField(
        upload_to="videos/hls/", blank=True, null=True)
    quality_levels = models.JSONField(default=list, blank=True)
    preview = models.FileField(upload_to="videos/previews/", blank=True)
    thumbnail = models.ImageField(upload_to="videos/thumbs/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        Represent a video by its title.
        """
        return self.title
