from rest_framework import serializers
from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'id', 'created_at', 'genre', 'title', 'description',
            'duration', 'available_resolutions',
            'thumbnail_image', 'preview_clip', 'hls_playlist', 'video_file'
        ]
        read_only_fields = ['id', 'created_at']
