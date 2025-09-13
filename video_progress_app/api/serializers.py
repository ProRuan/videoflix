# Third-party suppliers
from rest_framework import serializers

# Local imports
from video_app.models import Video
from ..models import VideoProgress


class VideoProgressCreateSerializer(serializers.Serializer):
    """Create progress for the authenticated user."""
    video_id = serializers.IntegerField()
    last_position = serializers.FloatField()

    def validate(self, attrs):
        if attrs["last_position"] < 0:
            raise serializers.ValidationError("Invalid last_position.")
        if not Video.objects.filter(id=attrs["video_id"]).exists():
            raise serializers.ValidationError({"video_id": "Video not found."})
        return attrs

    def create(self, validated):
        user_id = self.context["request"].user.id
        obj, _ = VideoProgress.objects.update_or_create(
            user_id=user_id,
            video_id=validated["video_id"],
            defaults={"last_position": validated["last_position"]},
        )
        return obj


class VideoProgressDetailSerializer(serializers.ModelSerializer):
    """Payload for read/update/delete."""
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    video_id = serializers.IntegerField(source="video.id", read_only=True)

    class Meta:
        model = VideoProgress
        fields = ("id", "user_id", "video_id", "last_position")
