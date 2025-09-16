# Third-party suppliers
from django.contrib.auth import get_user_model

# Local imports
from video_app.models import Video
from video_progress_app.models import VideoProgress


def make_user(email: str = "u@mail.com", active: bool = True):
    """Make a test user."""
    User = get_user_model()
    u = User.objects.create_user(email=email, password="Pwd12345!")
    if not active:
        u.is_active = False
        u.save(update_fields=["is_active"])
    return u


def make_video(title: str = "Wolf", genre: str = "Nature", **kw) -> Video:
    """Make a test video."""
    return Video.objects.create(title=title, genre=genre, **kw)


def make_progress(user, video, last: float = 12.5, rel: float | None = None):
    """Make a test video progress."""
    return VideoProgress.objects.create(
        user=user,
        video=video,
        last_position=last,
        relative_position=rel if rel is not None else 0.0,
    )
