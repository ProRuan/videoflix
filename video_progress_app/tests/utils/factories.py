# Third-party suppliers
from django.contrib.auth import get_user_model

# Local imports
from video_app.models import Video
from video_progress_app.models import VideoProgress


def make_user(email="u@mail.com", active=True):
    User = get_user_model()
    u = User.objects.create_user(email=email, password="Pwd12345!")
    if not active:
        u.is_active = False
        u.save(update_fields=["is_active"])
    return u


def make_video(title="Wolf", genre="Nature"):
    return Video.objects.create(title=title, genre=genre)


def make_progress(user, video, last=12.5):
    return VideoProgress.objects.create(
        user=user, video=video, last_position=last
    )
