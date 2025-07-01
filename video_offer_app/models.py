from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import date


class Video(models.Model):
    created_at = models.DateField(default=date.today)
    genre = models.CharField(max_length=80, default='')
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    video_file = models.FileField(
        upload_to='videos/original/', blank=True, null=True)
    hls_playlist = models.FileField(
        upload_to='videos/hls/',    blank=True, null=True)
    preview_clip = models.FileField(
        upload_to='videos/preview/', blank=True, null=True)
    thumbnail_image = models.ImageField(
        upload_to='videos/thumbs/', blank=True, null=True)
    sprite_sheet = models.FileField(upload_to='videos/sprites/', blank=True, null=True,
                                    help_text="Contact sheet image generated automatically")
    duration = models.IntegerField(
        blank=True, null=True, help_text="Duration in seconds")
    available_resolutions = ArrayField(
        models.CharField(max_length=10),
        default=list,
        blank=True,
        help_text="List of HLS resolutions generated, e.g. ['1080p','720p']"
    )

    def __str__(self):
        return self.title


# from django.db import models
# from datetime import date


# class Video(models.Model):
#     created_at = models.DateField(default=date.today)
#     genre = models.CharField(max_length=80, default='')
#     title = models.CharField(max_length=80)
#     description = models.CharField(max_length=500)
#     video_file = models.FileField(
#         upload_to='videos/original/', blank=True, null=True)
#     hls_playlist = models.FileField(
#         upload_to='videos/hls/',    blank=True, null=True)
#     preview_clip = models.FileField(
#         upload_to='videos/preview/', blank=True, null=True)
#     thumbnail_image = models.ImageField(
#         upload_to='videos/thumbs/', blank=True, null=True)
#     sprite_sheet = models.FileField(upload_to='videos/sprites/', blank=True,
#                                     null=True, help_text="Contact sheet image generated automatically")
#     duration = models.IntegerField(
#         blank=True, null=True, help_text="Duration in seconds")

#     def __str__(self):
#         return self.title


# from django.db import models
# from datetime import date


# class Video(models.Model):
#     created_at = models.DateField(default=date.today)
#     genre = models.CharField(max_length=80, default='')
#     title = models.CharField(max_length=80)
#     description = models.CharField(max_length=500)
#     video_file = models.FileField(
#         upload_to='videos/original/', blank=True, null=True)
#     hls_playlist = models.FileField(
#         upload_to='videos/hls/',    blank=True, null=True)
#     preview_clip = models.FileField(
#         upload_to='videos/preview/', blank=True, null=True)
#     thumbnail_image = models.ImageField(
#         upload_to='videos/thumbs/', blank=True, null=True)
#     duration = models.IntegerField(
#         blank=True, null=True, help_text="Duration in seconds")

#     def __str__(self):
#         return self.title


# from django.db import models
# from datetime import date


# class Video(models.Model):
#     created_at = models.DateField(default=date.today)
#     genre = models.CharField(max_length=80, default='')
#     title = models.CharField(max_length=80)
#     description = models.CharField(max_length=500)
#     video_file = models.FileField(
#         upload_to='videos/original/', blank=True, null=True)
#     hls_playlist = models.FileField(
#         upload_to='videos/hls/',    blank=True, null=True)
#     preview_clip = models.FileField(
#         upload_to='videos/preview/', blank=True, null=True)
#     thumbnail_image = models.ImageField(
#         upload_to='videos/thumbs/', blank=True, null=True)

#     def __str__(self):
#         return self.title
