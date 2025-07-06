# Third-party suppliers
import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Local imports
from .models import Video
from .tasks import (
    generate_hls,
    generate_preview,
    generate_sprite_sheet,
    generate_thumbnail,
)
from .utils import get_video_duration


@receiver(post_save, sender=Video)
def on_video_saved(sender, instance, created, **kwargs):
    """
    Compute duration and enqueue processing on creation.
    """
    if not created or not instance.video_file:
        return
    duration = get_video_duration(instance.video_file.path)
    if duration is not None:
        Video.objects.filter(pk=instance.pk).update(duration=duration)
    q = django_rq.get_queue('default')
    q.enqueue(generate_hls, instance.id)
    q.enqueue(generate_preview, instance.id, 10)
    q.enqueue(generate_thumbnail, instance.id)
    q.enqueue(generate_sprite_sheet, instance.id, 10, 5)


@receiver(post_delete, sender=Video)
def on_video_deleted(sender, instance, **kwargs):
    """
    Clean up files related to a Video instance.
    """
    storage = instance.video_file.storage
    for field in (
        instance.video_file,
        instance.hls_playlist,
        instance.preview_clip,
        instance.thumbnail_image,
        instance.sprite_sheet,
    ):
        try:
            storage.delete(field.name)
        except Exception:
            pass
