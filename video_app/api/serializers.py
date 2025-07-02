# video_offer_app/serializers.py

from rest_framework import serializers
from video_app.models import Video
import os

from video_app.models import VideoProgress


class VideoSerializer(serializers.ModelSerializer):
    # Add a read‑only method field listing the available HLS variants
    available_resolutions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Video
        # Expose everything, but make some fields read-only
        fields = [
            'id', 'created_at', 'genre', 'title', 'description', 'video_file',
            'duration', 'hls_playlist', 'preview_clip', 'thumbnail_image',
            'available_resolutions',
        ]
        read_only_fields = (
            'id', 'created_at', 'duration',
            'hls_playlist', 'preview_clip', 'thumbnail_image',
            'available_resolutions',
        )

    def get_available_resolutions(self, obj):
        """
        Look in MEDIA_ROOT/videos/hls/<base>/ and list each sub‑folder
        (i.e. ['1080p','720p','360p','120p']).
        """
        if not obj.hls_playlist:
            return []
        # derive the base dir from the playlist URL
        # e.g. /media/videos/hls/<base>/<base>.m3u8 → MEDIA_ROOT/videos/hls/<base>/
        from django.conf import settings
        rel_path = obj.hls_playlist.name  # videos/hls/<base>/<base>.m3u8
        hls_dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT, rel_path))
        try:
            return sorted(
                name for name in os.listdir(hls_dir)
                if os.path.isdir(os.path.join(hls_dir, name))
            )
        except FileNotFoundError:
            return []


class VideoProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProgress
        fields = ('user', 'video', 'last_position', 'updated_at')
        read_only_fields = ('user', 'updated_at')


# from rest_framework import serializers
# from video_offer_app.models import Video


# # call all fields literally
# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = '__all__'
#         read_only_fields = ('hls_playlist', 'preview_clip',
#                             'thumbnail_image', 'created_at')


# is working
# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = ['id', 'created_at', 'title', 'description', 'video_file']
#         read_only_fields = ['id', 'created_at']


# validate fields or set default and required!

# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = ['id', 'title', 'description', 'video_file', 'created_at']

#     def validate_title(self, value):
#         if not value:
#             raise serializers.ValidationError("Title cannot be empty.")
#         return value
