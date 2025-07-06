# Third-party suppliers
from django.contrib import admin

# Local imports
from .models import VideoProgress


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    """
    Represents a video progress admin.
    """
    list_display = ('id', 'user', 'video', 'last_position', 'updated_at')
    list_filter = ('user', 'video')
    search_fields = ('user__email', 'video__title')
    ordering = ('-updated_at',)
