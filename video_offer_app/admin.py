# from django.contrib import admin

# from .models import Video

# Register your models here.

# admin.site.register(Video)

# video_offer_app/admin.py

# from django.contrib import admin
# from .models import Video


# @admin.register(Video)
# class VideoAdmin(admin.ModelAdmin):
#     # Show these columns in the list view (optional)
#     list_display = ('title', 'created_at', 'duration', 'genre')
#     # Make created_at and duration read‑only in both the add and change forms
#     readonly_fields = ('created_at', 'duration')
#     # (You can still filter or search on them if you like)
#     list_filter = ('genre', 'created_at')
#     search_fields = ('title', 'description')

#     # If you want to prevent the user from *setting* them at all on create,
#     # you can also exclude them from the “add” form:
#     def get_exclude(self, request, obj=None):
#         if obj is None:  # adding a new Video
#             return ('created_at', 'duration')
#         return super().get_exclude(request, obj)

#     # Otherwise, readonly_fields alone will render them as uneditable.


from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'duration',
                    'genre', 'available_resolutions')
    readonly_fields = ('created_at', 'duration',
                       'available_resolutions', 'sprite_sheet')
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'description')


# was not working
# ---------------
# from django.contrib import admin
# from .models import Video

# @admin.register(Video)
# class VideoAdmin(admin.ModelAdmin):
#     list_display    = ('title', 'created_at', 'duration', 'genre', 'available_resolutions')
#     readonly_fields = ('created_at', 'duration', 'available_resolutions', 'sprite_sheet')
#     list_filter     = ('genre', 'created_at')
#     search_fields   = ('title', 'description')

#     def get_available_resolutions(self, obj):
#         if not obj.hls_playlist:
#             return []
#         from django.conf import settings
#         rel = obj.hls_playlist.name
#         hls_dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT, rel))
#         try:
#             return ', '.join(sorted(
#                 name for name in os.listdir(hls_dir)
#                 if os.path.isdir(os.path.join(hls_dir, name))
#             ))
#         except Exception:
#             return ''
#     get_available_resolutions.short_description = 'Resolutions'
