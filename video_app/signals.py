# Standard libraries

# Third-party suppliers
from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq

# Local imports
from .models import Video
from .tasks import process_video


@receiver(post_save, sender=Video)
def enqueue_processing(sender, instance: Video, created: bool, **kwargs):
    """Queue processing when a video file exists."""
    if instance.video_file and (created or not instance.hls_playlist):
        django_rq.enqueue(process_video, instance.id)
