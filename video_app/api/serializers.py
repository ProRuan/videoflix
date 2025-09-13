# Third-party suppliers
from rest_framework import serializers

# Local imports
from ..models import Video


class VideoListItemSerializer(serializers.ModelSerializer):
    """Minimal video fields for list."""
    class Meta:
        model = Video
        fields = ("id", "title", "genre", "description",
                  "preview", "thumbnail", "created_at")


class VideoDetailSerializer(serializers.ModelSerializer):
    """Full video details for detail view."""
    class Meta:
        model = Video
        fields = ("id", "title", "genre", "description", "duration",
                  "hls_playlist", "quality_levels", "preview",
                  "thumbnail", "created_at")
