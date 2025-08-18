from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


class BaseToken(models.Model):
    """Abstract base token: fields only (no methods)."""
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    lifetime = models.DurationField()
    used = models.BooleanField(default=False)

    class Meta:
        abstract = True


class AccountActivationToken(BaseToken):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="account_activation_token"
    )
    lifetime = models.DurationField(default=timedelta(hours=24))


class AccountDeletionToken(BaseToken):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="account_deletion_token"
    )
    lifetime = models.DurationField(default=timedelta(hours=24))


class PasswordResetToken(BaseToken):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="password_reset_token"
    )
    lifetime = models.DurationField(default=timedelta(hours=1))
