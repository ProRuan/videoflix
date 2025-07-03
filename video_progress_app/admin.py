from django.contrib import admin
from .models import VideoProgress


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'last_position', 'updated_at')
    list_filter = ('user', 'video')
    search_fields = ('user__email', 'video__title')
    ordering = ('-updated_at',)
