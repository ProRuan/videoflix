# Standard libraries

# Third-party suppliers
from django.contrib import admin

# Local imports
from token_app.models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    """Admin for tokens."""
    list_display = ["value", "type", "user", "used", "expired_at"]
    list_filter = ["type", "used"]
    search_fields = ["value", "user__email"]
    readonly_fields = ["created_at"]
