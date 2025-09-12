# Standard libraries

# Third-party suppliers
from django.apps import AppConfig

# Local imports


class VideoAppConfig(AppConfig):
    """
    App config to wire signals on app ready.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "video_app"

    def ready(self) -> None:
        """
        Import signals when app is ready.
        """
        from . import signals  # noqa: F401
