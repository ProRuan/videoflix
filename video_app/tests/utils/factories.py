# video_app/tests/utils/factories.py
# Standard libraries
from datetime import datetime, timedelta, timezone as dtz
from io import BytesIO

# Third-party suppliers
from django.core.files.base import ContentFile
from django.urls import reverse
from knox.models import AuthToken

# Local imports
from django.contrib.auth import get_user_model
from video_app.models import Video


def make_user(email: str = "u@mail.com") -> object:
    """
    Create and return a user with password.
    """
    User = get_user_model()
    return User.objects.create_user(email=email, password="pass1234")


def make_token(user) -> str:
    """
    Create and return a Knox token for user.
    """
    _, token = AuthToken.objects.create(user)
    return token


def make_video(title: str = "Clip", genre: str = "Action") -> Video:
    """
    Create and return a minimal Video instance.
    """
    dummy = ContentFile(b"fake", name="dummy.mp4")
    return Video.objects.create(title=title, genre=genre, video_file=dummy)


def set_created_at(obj: Video, days_ago: int = 0) -> None:
    """
    Update created_at to 'now - days_ago' for ordering tests.
    """
    when = datetime.now(dtz.utc) - timedelta(days=days_ago)
    Video.objects.filter(id=obj.id).update(created_at=when)
