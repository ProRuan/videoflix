# Standard libraries
import os

# Third-party suppliers
import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Local imports
from .models import Video
from .tasks import convert_480p


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('video successfully saved')
    if created:
        print('new video created')
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)


# delete converted videos as well!
@receiver(post_delete, sender=Video)
def auto_delete_video_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
