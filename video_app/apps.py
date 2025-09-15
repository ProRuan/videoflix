# Third-party suppliers
from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    """Video app config that wires signals on startup."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "video_app"

    def ready(self) -> None:
        """Import video signals when Django is ready."""
        from . import signals
