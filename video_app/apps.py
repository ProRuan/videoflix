# Third-party suppliers
from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    """
    Video App Configuration including signals.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_app'

    def ready(self):
        """
        Ready the video_app signals.
        """
        from . import signals
