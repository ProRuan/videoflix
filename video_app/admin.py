# video_app/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin configuration for Video model, with distinct layouts for Add and Change views.
    """
    # Fields to display/edit on Change view
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'genre', 'video_file')
        }),
        (_('Video info'), {
            'fields': (
                'hls_playlist', 'preview_clip', 'thumbnail_image',
                'sprite_sheet', 'duration', 'available_resolutions', 'created_at'
            ),
            'classes': ('wide',),  # collapsed by default
            'description': _('Auto‑generated upon upload. Generation time may vary based on video length.'),
        }),
    )

    # Fields to show on the Add form (omit auto-generated)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'genre', 'description', 'video_file'),
        }),
    )

    readonly_fields = (
        'hls_playlist', 'preview_clip', 'thumbnail_image',
        'sprite_sheet', 'duration', 'available_resolutions', 'created_at'
    )

    list_display = ('title', 'genre', 'duration',
                    'available_resolutions', 'created_at')
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'genre', 'description')
    ordering = ('-created_at',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            # Use add_fieldsets on add
            return self.add_fieldsets
        return self.fieldsets

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            # On add, no fields are read-only
            return ()
        return ('video_file', ) + self.readonly_fields
