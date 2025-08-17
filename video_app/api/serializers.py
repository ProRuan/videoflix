# Third-party suppliers
from rest_framework import serializers

# Local imports
from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Represents a video serializer for listing videos.
    """
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'genre', 'preview_clip',
            'thumbnail_image', 'sprite_sheet', 'created_at',
        ]
        read_only_fields = [
            'id', 'preview_clip' 'thumbnail_image',
            'sprite_sheet', 'created_at'
        ]


class VideoDetailSerializer(serializers.ModelSerializer):
    """
    Represents a video detail serializer containing video information.
    """
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'genre',
            'description', 'video_file', 'hls_playlist',
            'preview_clip', 'thumbnail_image', 'sprite_sheet',
            'duration', 'available_resolutions', 'created_at',
        ]
        read_only_fields = [
            'id', 'video_file', 'hls_playlist',
            'preview_clip', 'thumbnail_image', 'sprite_sheet',
            'duration', 'available_resolutions', 'created_at'
        ]
