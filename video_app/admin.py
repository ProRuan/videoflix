# Third-party suppliers
from django.contrib import admin
from django.utils.translation import gettext_lazy

# Local imports
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin configuration for Video model with distinct layouts for Add and
    Change views.
    """

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'genre', 'video_file')
        }),
        (gettext_lazy('Video info'), {
            'fields': (
                'hls_playlist', 'preview_clip', 'thumbnail_image',
                'sprite_sheet', 'duration', 'available_resolutions',
                'created_at'
            ),
            'classes': ('wide',),
            'description': gettext_lazy(
                'Auto‑generated upon upload. '
                'Generation time may vary based on video length.'
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'genre', 'description', 'video_file'),
        }),
    )

    readonly_fields = (
        'hls_playlist', 'preview_clip', 'thumbnail_image',
        'sprite_sheet', 'duration', 'available_resolutions',
        'created_at'
    )

    list_display = (
        'title', 'genre', 'duration',
        'available_resolutions', 'created_at'
    )
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'genre', 'description')
    ordering = ('-created_at',)

    def get_fieldsets(self, request, obj=None):
        """
        Get fieldsets depending on the view page (Add, Change).
        """
        if not obj:
            return self.add_fieldsets
        return self.fieldsets

    def get_readonly_fields(self, request, obj=None):
        """
        Get readonly_fields depending on the view page (Add, Change).
        """
        if not obj:
            return ()
        return ('video_file', ) + self.readonly_fields
