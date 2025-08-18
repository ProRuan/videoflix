from django.contrib import admin
from django.utils import timezone
from .models import (
    AccountActivationToken,
    AccountDeletionToken,
    PasswordResetToken,
)


class BaseTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expired_at", "used")
    search_fields = ("user__email", "token")

    def expired_at(self, obj):
        """Return created_at + lifetime as localized datetime (or None)."""
        if not getattr(obj, "created_at", None) or not getattr(obj, "lifetime", None):
            return None
        exp = obj.created_at + obj.lifetime
        return timezone.localtime(exp)

    expired_at.admin_order_field = "created_at"
    expired_at.short_description = "expired_at"


@admin.register(AccountActivationToken)
class AccountActivationTokenAdmin(BaseTokenAdmin):
    pass


@admin.register(AccountDeletionToken)
class AccountDeletionTokenAdmin(BaseTokenAdmin):
    pass


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(BaseTokenAdmin):
    pass


# @admin.register(AccountActivationToken)
# class AccountActivationTokenAdmin(admin.ModelAdmin):
#     list_display = ("user", "token", "created_at", "used")
#     search_fields = ("user__email", "token")


# @admin.register(AccountDeletionToken)
# class AccountDeletionTokenAdmin(admin.ModelAdmin):
#     list_display = ("user", "token", "created_at", "used")
#     search_fields = ("user__email", "token")


# @admin.register(PasswordResetToken)
# class PasswordResetTokenAdmin(admin.ModelAdmin):
#     list_display = ("user", "token", "created_at", "used")
#     search_fields = ("user__email", "token")
