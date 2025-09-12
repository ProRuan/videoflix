# Standard libraries

# Third-party suppliers
from django.contrib import admin

# Local imports
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin config for Video list and detail pages.
    """
    list_display = ("title", "genre", "duration", "video_file", "created_at")
    search_fields = ("title", "genre", "description")
    list_filter = ("genre", "created_at")
