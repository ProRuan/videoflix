from django.apps import AppConfig


class VideoOfferAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_offer_app'

    def ready(self):
        from . import signals
