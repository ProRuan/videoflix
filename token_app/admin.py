from django.contrib import admin
from .models import (
    AccountActivationToken,
    AccountDeletionToken,
    PasswordResetToken,
)


@admin.register(AccountActivationToken)
class AccountActivationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "used")
    search_fields = ("user__email", "token")


@admin.register(AccountDeletionToken)
class AccountDeletionTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "used")
    search_fields = ("user__email", "token")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "used")
    search_fields = ("user__email", "token")
