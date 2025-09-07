# Standard libraries

# Third-party suppliers
from django.conf import settings
from django.db import models

# Local imports


class Token(models.Model):
    """Represents a short-lived token with a specific purpose."""
    TYPE_ACTIVATION = "account_activation"
    TYPE_DELETION = "account_deletion"
    TYPE_AUTH = "authentication"
    TYPE_RESET = "password_reset"

    TYPE_CHOICES = [
        (TYPE_ACTIVATION, "Account Activation"),
        (TYPE_DELETION, "Account Deletion"),
        (TYPE_AUTH, "Authentication"),
        (TYPE_RESET, "Password Reset"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    value = models.CharField(max_length=64, unique=True)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["type", "user", "used", "expired_at"])]

    def __str__(self):
        """Return token type and user email."""
        return f"{self.type} • {self.user_id}"
