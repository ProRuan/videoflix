# Third-party suppliers
from rest_framework import serializers

# Local imports
from video_progress_app.models import VideoProgress
from video_progress_app.utils import (
    exceeds_video_duration,
    get_video_instance,
)


class VideoProgressSerializer(serializers.ModelSerializer):
    """
    Represents a video progress serializer.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VideoProgress
        fields = ['id', 'user', 'video', 'last_position', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate_last_position(self, value):
        """
        Check last_position for being non-negative and within video duration.
        """
        if value < 0:
            raise serializers.ValidationError(
                "last_position must be non-negative."
            )
        video = get_video_instance(self)
        if exceeds_video_duration(self, value, video):
            raise serializers.ValidationError(
                "last_position exceeds video duration."
            )
        return value
