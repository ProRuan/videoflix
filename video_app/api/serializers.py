# Third-party suppliers
from rest_framework import serializers

# Local imports
from video_app.models import Video
from video_app.utils import get_resolution_urls


class VideoSerializer(serializers.ModelSerializer):
    """
    Represents a video serializer for listing videos.
    """
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'genre', 'description', 'preview_clip',
            'thumbnail_image', 'sprite_sheet', 'created_at',
        ]
        read_only_fields = [
            'id', 'preview_clip' 'thumbnail_image',
            'sprite_sheet', 'created_at'
        ]


class VideoDetailSerializer(serializers.ModelSerializer):
    """
    Full detail serializer including preview_clip and the resolution map.
    available_resolutions is returned as a mapping name -> playlist URL.
    """
    preview_clip = serializers.FileField(read_only=True)
    available_resolutions = serializers.SerializerMethodField()

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

    def get_available_resolutions(self, obj):
        # Pass request from serializer context so absolute URLs are built
        request = self.context.get('request')
        return get_resolution_urls(obj, request=request)
