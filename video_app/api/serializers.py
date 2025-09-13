# Third-party suppliers
from rest_framework import serializers

# Local imports
from ..models import Video


class VideoListItemSerializer(serializers.ModelSerializer):
    """Minimal video fields for list, plus progress."""
    last_position = serializers.FloatField(read_only=True, default=0.0)
    relative_position = serializers.FloatField(read_only=True, default=0.0)

    class Meta:
        model = Video
        fields = ("id", "title", "genre", "description",
                  "preview", "thumbnail", "created_at",
                  "last_position", "relative_position")


class VideoDetailSerializer(serializers.ModelSerializer):
    """Full video details for detail view + last_position."""
    last_position = serializers.FloatField(read_only=True, default=0.0)

    class Meta:
        model = Video
        fields = ("id", "title", "genre", "description", "duration",
                  "hls_playlist", "quality_levels", "preview",
                  "thumbnail", "created_at", "last_position")
