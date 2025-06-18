from rest_framework import serializers
from video_offer_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'video_file']
        read_only_fields = ['id', 'created_at']
