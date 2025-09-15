# Local imports
from video_app.models import Video


def get_video_instance(serializer):
    """
    Get Video from incoming payload or serializer instance.
    """
    video_id = serializer.initial_data.get("video")
    if video_id:
        return Video.objects.filter(pk=video_id).first()
    if serializer.instance:
        return getattr(serializer.instance, "video", None)
    return None


def exceeds_video_duration(value, video):
    """
    Check value for exceeding the video´s known duration (seconds).
    """
    return bool(video and video.duration and value > video.duration)


def get_relative_position(last: float, dur: float) -> float:
    """Get the relative position (percent) of a video progress."""
    if not dur or dur <= 0:
        return 0.0
    return round(last / dur * 100.0, 2)
