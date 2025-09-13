# Standard libraries
from typing import Any

# Third-party suppliers
from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "video_app"

    def ready(self) -> None:
        from . import signals  # noqa: F401
