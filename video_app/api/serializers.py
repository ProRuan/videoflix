# Third-party suppliers
from rest_framework import serializers

# Local imports
from video_app.models import Video


class OmitNoneModelSerializer(serializers.ModelSerializer):
    """
    Class representing an omit none model serializer.

    Drops fields that are None from the response.
    """

    def to_representation(self, instance):
        """Take the video fields which are not None only."""
        data = super().to_representation(instance)
        return {k: v for k, v in data.items() if v is not None}


class VideoListItemSerializer(OmitNoneModelSerializer):
    """
    Class representing a video list item serializer.

    Can include optional video progress fields.
    """
    progress_id = serializers.IntegerField(required=False, allow_null=True)
    relative_position = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Video
        fields = ("id", "title", "genre", "description",
                  "preview", "thumbnail", "created_at",
                  "progress_id", "relative_position")


class VideoDetailSerializer(OmitNoneModelSerializer):
    """
    Class representing a video detail serializer.

    Can include optional video progress fields.
    """
    progress_id = serializers.IntegerField(required=False, allow_null=True)
    last_position = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Video
        fields = ("id", "title", "genre", "description", "duration",
                  "hls_playlist", "quality_levels", "preview",
                  "thumbnail", "created_at", "progress_id",
                  "last_position")
