# Standard libraries

# Third-party suppliers
from rest_framework import serializers

# Local imports
from ..models import Video
from ..utils import abs_url


class VideoItemSerializer(serializers.ModelSerializer):
    """
    Public video serializer with absolute URLs for media fields.
    """
    hls_playlist = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    quality_levels = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            "id", "title", "genre", "description", "duration",
            "hls_playlist", "quality_levels", "preview",
            "thumbnail", "created_at",
        )

    def get_hls_playlist(self, obj):
        req = self.context.get("request")
        return abs_url(req, obj.hls_playlist) if req else None

    def get_preview(self, obj):
        req = self.context.get("request")
        return abs_url(req, obj.preview) if req else None

    def get_thumbnail(self, obj):
        req = self.context.get("request")
        return abs_url(req, obj.thumbnail) if req else None

    def get_quality_levels(self, obj):
        req = self.context.get("request")
        levels = obj.quality_levels or []
        if not req:
            return levels
        out = []
        for item in levels:
            src = abs_url(req, item.get("source"))
            out.append({"label": item.get("label", ""), "source": src})
        return out
