# Standard libraries
import math

# Third-party suppliers
from django.contrib import admin

# Local imports
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin for Video model."""
    list_display = (
        "title", "genre", "duration_whole", "quality_labels",
        "video_file", "created_at",
    )
    readonly_fields = (
        "duration_whole", "quality_labels", "hls_playlist",
        "preview", "thumbnail", "created_at",
    )
    fieldsets = (
        ("Basic info", {"fields": ("title", "genre",
                                   "description", "video_file")}),
        ("Generated assets", {
            "fields": ("duration_whole", "quality_labels", "hls_playlist",
                       "preview", "thumbnail"),
            "description": "Automatically generated fields.",
        }),
        ("Dates", {"fields": ("created_at",)}),
    )

    def duration_whole(self, obj) -> int | str:
        """Return duration rounded up to a whole second."""
        if obj.duration is None:
            return "-"
        return math.ceil(obj.duration)
    duration_whole.short_description = "Duration"

    def quality_labels(self, obj) -> str:
        """Return labels like '1080p, 720p, 360p, 144p'."""
        parts = [q.get("label", "") for q in (obj.quality_levels or [])]
        return ", ".join([p for p in parts if p]) or "-"
    quality_labels.short_description = "Quality levels"
