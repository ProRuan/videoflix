from rest_framework import serializers
from video_progress_app.models import VideoProgress
from video_app.models import Video


class VideoProgressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VideoProgress
        fields = ['id', 'user', 'video', 'last_position', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate_last_position(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "last_position must be non-negative.")
        # check against video duration if available
        video = self.initial_data.get('video')
        try:
            vid = Video.objects.get(pk=video)
        except Video.DoesNotExist:
            raise serializers.ValidationError("Video not found.")
        if vid.duration is not None and value > vid.duration:
            raise serializers.ValidationError(
                "last_position exceeds video duration.")
        return value
