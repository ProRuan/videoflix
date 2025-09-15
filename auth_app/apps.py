# Third-party suppliers
from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Auth app config that wires signals on startup."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"

    def ready(self) -> None:
        """Import auth signals when Django is ready."""
        from . import signals
