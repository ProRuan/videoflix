# Third-party suppliers
from django.utils import timezone

# Local imports
from video_app.models import Video


def make_video(**kwargs) -> Video:
    """Make Video with defaults."""
    now = timezone.now()
    defaults = dict(
        title="Wolf",
        genre="Nature",
        description="",
        duration=0.0,
        created_at=now,
    )
    defaults.update(kwargs)
    return Video.objects.create(**defaults)
