# Standard libraries
import os

# Third-party packages
import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Local imports
from .models import Video
from .tasks import convert_480p, convert_120p, convert_360p, convert_720p, convert_1080p, generate_thumbnail


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video successfully saved')
    if created and instance.video_file:
        print('New video created')
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)
        queue.enqueue(convert_120p, instance.video_file.path)
        queue.enqueue(convert_360p, instance.video_file.path)
        queue.enqueue(convert_720p, instance.video_file.path)
        queue.enqueue(convert_1080p, instance.video_file.path)
        queue.enqueue(generate_thumbnail, instance.video_file.path)


@receiver(post_delete, sender=Video)
def auto_delete_video_file_on_delete(sender, instance, **kwargs):
    """
    Delete original and converted video files from the filesystem
    when a Video instance is deleted.
    """
    if instance.video_file:
        original_path = instance.video_file.path
        if os.path.isfile(original_path):
            os.remove(original_path)

        # Remove the 480p version as well
        base, _ = os.path.splitext(original_path)
        converted_path = base + '_480p.mp4'
        if os.path.isfile(converted_path):
            os.remove(converted_path)
