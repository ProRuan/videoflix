# Standard libraries

# Third-party suppliers
from django.apps import AppConfig

# Local imports


class AuthAppConfig(AppConfig):
    """Auth app config that wires signals on startup."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"

    def ready(self) -> None:
        # Import signals to register handlers.
        from . import signals  # noqa: F401
