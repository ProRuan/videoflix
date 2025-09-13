# Third-party suppliers
from rest_framework import serializers

# Local imports
from video_app.models import Video
from ..models import VideoProgress


def _rel(last: float, dur: float) -> float:
    if not dur or dur <= 0:
        return 0.0
    return round(last / dur * 100.0, 2)


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
        video = Video.objects.get(id=validated["video_id"])
        rel = _rel(validated["last_position"], video.duration)
        obj, _ = VideoProgress.objects.update_or_create(
            user_id=user_id, video_id=video.id,
            defaults={"last_position": validated["last_position"],
                      "relative_position": rel},
        )
        return obj


class VideoProgressDetailSerializer(serializers.ModelSerializer):
    """Payload for read/update/delete."""
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    video_id = serializers.IntegerField(source="video.id", read_only=True)

    class Meta:
        model = VideoProgress
        fields = ("id", "user_id", "video_id",
                  "last_position", "relative_position")
