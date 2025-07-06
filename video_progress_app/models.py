# Third-party suppliers
from django.contrib.auth import get_user_model
from django.db import models

# Local imports
from video_app.models import Video

User = get_user_model()


class VideoProgress(models.Model):
    """
    Represents a user-related video progress.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='video_progress'
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE,
        related_name='progress_entries'
    )
    last_position = models.IntegerField(
        default=0, help_text='Last playback time in seconds',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-updated_at']

    def __str__(self):
        """
        Get a string representing a video progress.
        """
        return f"{self.user} @ {self.last_position:.1f}s of {self.video}"
