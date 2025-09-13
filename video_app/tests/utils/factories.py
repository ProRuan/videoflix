# Standard libraries
from datetime import timedelta

# Third-party suppliers
from django.utils import timezone

# Local imports
from video_app.models import Video


def make_video(**kwargs) -> Video:
    """Factory for Video with sane defaults."""
    now = timezone.now()
    defaults = dict(
        title="Sample",
        genre="Drama",
        description="",
        duration=0.0,
        created_at=now,
    )
    defaults.update(kwargs)
    return Video.objects.create(**defaults)
