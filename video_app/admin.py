from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'genre', 'duration',
        'available_resolutions', 'created_at',
    )
    readonly_fields = (
        'hls_playlist', 'preview_clip', 'thumbnail_image',
        'sprite_sheet', 'duration', 'available_resolutions',
        'created_at'
    )
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'description')
