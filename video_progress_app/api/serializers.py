# Third-party suppliers
from rest_framework import serializers

# Local imports
from video_app.models import Video
from video_progress_app.models import VideoProgress
from video_progress_app.utils import get_relative_position


class VideoProgressCreateSerializer(serializers.Serializer):
    """
    Class representing a video progress create serializer.

    Creates a video progress.
    """
    video_id = serializers.IntegerField()
    last_position = serializers.FloatField()

    def validate(self, attrs):
        """Check video for existence and video progress for validity."""
        if attrs["last_position"] < 0:
            raise serializers.ValidationError("Invalid last_position.")
        if not Video.objects.filter(id=attrs["video_id"]).exists():
            raise serializers.ValidationError({"video_id": "Video not found."})
        return attrs

    def create(self, validated):
        """Create video progress."""
        user_id = self.context["request"].user.id
        video = Video.objects.get(id=validated["video_id"])
        rel_pos = get_relative_position(
            validated["last_position"], video.duration)
        obj, _ = VideoProgress.objects.update_or_create(
            user_id=user_id, video_id=video.id,
            defaults={"last_position": validated["last_position"],
                      "relative_position": rel_pos},
        )
        return obj


class VideoProgressUpdateSerializer(serializers.ModelSerializer):
    """
    Class representing a video progress update serializer.

    Validates and updates last_position and recalculates relative_position.
    """
    last_position = serializers.FloatField(required=True)

    class Meta:
        model = VideoProgress
        fields = ("last_position",)

    def validate_last_position(self, value):
        """Validate last position of a video progress."""
        if value < 0:
            raise serializers.ValidationError("This field is invalid.")
        return value

    def update(self, instance, validated):
        """Update the last position of a video progress."""
        dur = instance.video.duration or 0.0
        last_pos = validated["last_position"]
        instance.last_position = last_pos
        instance.relative_position = get_relative_position(last_pos, dur)
        instance.save(update_fields=["last_position", "relative_position"])
        return instance


class VideoProgressDetailSerializer(serializers.ModelSerializer):
    """
    Class representing a video progress detail serializer.

    Handles payload for update and deletion of a video progress.
    """
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    video_id = serializers.IntegerField(source="video.id", read_only=True)

    class Meta:
        model = VideoProgress
        fields = ("id", "user_id", "video_id",
                  "last_position", "relative_position")
