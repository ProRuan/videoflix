# Standard libraries

# Third-party suppliers
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import enqueue

# Local imports
from .models import Video
from .tasks import make_hls


@receiver(post_save, sender=Video)
def enqueue_make_hls(sender, instance: Video, created: bool, **kwargs) -> None:
    """Queue HLS build when a new Video with a file is created."""
    if created and instance.video_file:
        enqueue(make_hls, instance.id)
