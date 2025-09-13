# Third-party suppliers
from django.contrib import admin

# Local imports
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin for Video with readonly generated fields.
    """
    list_display = ("title", "genre", "duration", "video_file", "created_at")
    readonly_fields = (
        "duration", "hls_playlist", "quality_levels",
        "preview", "thumbnail", "created_at",
    )
    fieldsets = (
        ("Basic info", {
            "fields": ("title", "genre", "description", "video_file"),
        }),
        ("Generated assets", {
            "fields": (
                "duration", "hls_playlist", "quality_levels",
                "preview", "thumbnail",
            ),
            "description": "Those fields are automatically generated.",
        }),
        ("Dates", {"fields": ("created_at",)}),
    )
