from django.db import models
from django.contrib.auth import get_user_model

from video_app.models import Video

User = get_user_model()


class VideoProgress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='video_progress'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='progress_entries'
    )
    last_position = models.IntegerField(
        default=0,
        help_text='Last playback time in seconds'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this position was last updated'
    )

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user} @ {self.last_position:.1f}s of {self.video}"
