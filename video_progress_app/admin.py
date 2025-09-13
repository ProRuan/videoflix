# Third-party suppliers
from django.contrib import admin

# Local imports
from .models import VideoProgress


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    """Admin for video progress entries."""
    list_display = ("id", "user", "video", "last_position", "created_at")
    readonly_fields = ("created_at",)
