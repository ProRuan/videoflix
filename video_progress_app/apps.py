# Third-party suppliers
from django.apps import AppConfig


class VideoProgressAppConfig(AppConfig):
    """Video progress app config with default settings."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_progress_app'
