# Third-party suppliers
from django.contrib.auth import get_user_model
from django.db import models

# Local imports
from video_app.models import Video


class VideoProgress(models.Model):
    """
    User's last watched position (seconds) for a given Video.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    last_position = models.FloatField(default=0.0)
    relative_position = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"], name="uq_user_video_progress"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.video_id}@{self.last_position:.2f}s"
