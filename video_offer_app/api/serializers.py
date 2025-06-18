from rest_framework import serializers
from video_offer_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'video_file']
        read_only_fields = ['id', 'created_at']


# validate fields or set default and required!

# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = ['id', 'title', 'description', 'video_file', 'created_at']

#     def validate_title(self, value):
#         if not value:
#             raise serializers.ValidationError("Title cannot be empty.")
#         return value
