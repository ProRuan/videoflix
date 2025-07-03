from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import date
from .storage_backends import OverwriteStorage
from django.contrib.auth import get_user_model

User = get_user_model()

overwrite_storage = OverwriteStorage()


class Video(models.Model):
    created_at = models.DateField(default=date.today)
    genre = models.CharField(max_length=80, default='')
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    video_file = models.FileField(
        upload_to='videos/original/', storage=overwrite_storage, blank=True, null=True)
    hls_playlist = models.FileField(
        upload_to='videos/hls/',    storage=overwrite_storage, blank=True, null=True)
    preview_clip = models.FileField(
        upload_to='videos/preview/', storage=overwrite_storage, blank=True, null=True)
    thumbnail_image = models.ImageField(
        upload_to='videos/thumbs/', storage=overwrite_storage, blank=True, null=True)
    sprite_sheet = models.FileField(upload_to='videos/sprites/', storage=overwrite_storage, blank=True, null=True,
                                    help_text="Contact sheet image generated automatically")
    duration = models.IntegerField(
        blank=True, null=True, help_text="Duration in seconds")
    available_resolutions = ArrayField(
        models.CharField(max_length=10),
        default=list,
        blank=True,
        help_text="List of HLS resolutions generated, e.g. ['1080p','720p']"
    )

    def __str__(self):
        return self.title


# class VideoProgress(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='video_progress'
#     )
#     video = models.ForeignKey(
#         'Video',
#         on_delete=models.CASCADE,
#         related_name='progress_entries'
#     )
#     last_position = models.IntegerField(
#         default=0,
#         help_text='Last playback time in seconds'
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         help_text='When this position was last updated'
#     )

#     class Meta:
#         unique_together = ('user', 'video')
#         ordering = ['-updated_at']

#     def __str__(self):
#         return f"{self.user} @ {self.last_position:.1f}s of {self.video}"
