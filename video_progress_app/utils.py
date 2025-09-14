# Local imports
from video_app.models import Video


def get_video_instance(serializer):
    """
    Get Video from incoming payload (create) or the serializer instance.
    """
    video_id = serializer.initial_data.get("video")
    if video_id:
        return Video.objects.filter(pk=video_id).first()
    if serializer.instance:
        return getattr(serializer.instance, "video", None)
    return None


def exceeds_video_duration(value, video):
    """
    True if 'value' exceeds the video's known duration (seconds).
    """
    return bool(video and video.duration and value > video.duration)
