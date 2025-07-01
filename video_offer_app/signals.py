import os
import subprocess

import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.files import File

from .models import Video
from .tasks import (
    generate_hls,
    generate_preview,
    generate_thumbnail,
    generate_sprite_sheet
)


def _get_video_duration(path):
    """
    Use ffprobe to get the duration of the video in seconds (integer).
    """
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    try:
        # convert to float then int
        secs = float(result.stdout)
        return int(secs)
    except Exception:
        return None


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    # On creation, compute duration and enqueue processing
    if created and instance.video_file:
        # 1) Compute and save duration
        duration = _get_video_duration(instance.video_file.path)
        if duration is not None:
            Video.objects.filter(pk=instance.pk).update(duration=duration)

        # 2) Enqueue FFmpeg tasks
        q = django_rq.get_queue('default')
        q.enqueue(generate_hls,        instance.id)
        q.enqueue(generate_preview,    instance.id, 10)
        q.enqueue(generate_thumbnail,  instance.id)
        q.enqueue(generate_sprite_sheet,  instance.id, 10, 5)


@receiver(post_delete, sender=Video)
def cleanup_files(sender, instance, **kwargs):
    # Remove original and generated files from storage
    storage = instance.video_file.storage
    fields = [
        instance.video_file,
        instance.hls_playlist,
        instance.preview_clip,
        instance.thumbnail_image,
        instance.sprite_sheet
    ]
    for f in fields:
        try:
            storage.delete(f.name)
        except Exception:
            pass


# # video_offer_app/signals.py
# import django_rq
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models import Video
# from .tasks import generate_hls, generate_preview, generate_thumbnail


# @receiver(post_save, sender=Video)
# def video_post_save(sender, instance, created, **kwargs):
#     if created and instance.video_file:
#         q = django_rq.get_queue('default')
#         q.enqueue(generate_hls,        instance.id)
#         q.enqueue(generate_preview,    instance.id, 10)
#         q.enqueue(generate_thumbnail,  instance.id)


# @receiver(post_delete, sender=Video)
# def cleanup_files(sender, instance, **kwargs):
#     # Remove all media associated with this video
#     storage, fields = instance.video_file.storage, [
#         instance.video_file, instance.hls_playlist,
#         instance.preview_clip, instance.thumbnail_image
#     ]
#     for f in fields:
#         try:
#             storage.delete(f.name)
#         except Exception:
#             pass
