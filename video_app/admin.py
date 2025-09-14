# Standard libraries

# Third-party suppliers
from django.contrib import admin

# Local imports
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin for Video with human-friendly quality levels."""
    list_display = (
        "title", "genre", "duration", "quality_labels",
        "video_file", "created_at",
    )
    readonly_fields = (
        "duration", "quality_labels", "hls_playlist",
        "preview", "thumbnail", "created_at",
    )
    fieldsets = (
        ("Basic info", {"fields": ("title", "genre",
                                   "description", "video_file")}),
        ("Generated assets", {
            "fields": ("duration", "quality_labels", "hls_playlist",
                       "preview", "thumbnail"),
            "description": "Automatically generated fields.",
        }),
        ("Dates", {"fields": ("created_at",)}),
    )

    def quality_labels(self, obj) -> str:
        """Return labels like '1080p, 720p, 360p, 144p'."""
        parts = [q.get("label", "") for q in (obj.quality_levels or [])]
        return ", ".join([p for p in parts if p]) or "-"
    quality_labels.short_description = "Quality levels"
