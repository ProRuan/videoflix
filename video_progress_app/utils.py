# Local imports
from video_app.models import Video


def get_video_instance(self):
    """
    Get the associated video instance from payload or serializer instance.
    """
    video_id = self.initial_data.get('video')
    if video_id:
        return Video.objects.filter(pk=video_id).first()
    if self.instance:
        return getattr(self.instance, 'video', None)
    return None


def exceeds_video_duration(self, value, video):
    """
    Check if value exceeds an available video duration.
    """
    return bool(video and video.duration and value > video.duration)
