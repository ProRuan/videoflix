# Third-party suppliers
from django.apps import AppConfig


class TokenAppConfig(AppConfig):
    """Token app config with default settings."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'token_app'
