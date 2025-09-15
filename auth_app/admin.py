# Third-party suppliers
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""
    ordering = ["email"]
    search_fields = ["email"]
    list_display = ["email", "is_active", "is_staff", "is_superuser"]
    readonly_fields = ["last_login", "date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
         "fields": ("username", "first_name", "last_name")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser",
                       "groups", "user_permissions")
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )
