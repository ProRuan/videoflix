# Standard libraries

# Third-party suppliers
from django.apps import AppConfig

# Local imports


class VideoAppConfig(AppConfig):
    """AppConfig ensuring signals are registered."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "video_app"

    def ready(self) -> None:
        from . import signals  # noqa: F401
