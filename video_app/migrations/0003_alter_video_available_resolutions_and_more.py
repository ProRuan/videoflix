# Generated by Django 5.1.4 on 2025-07-03 20:46

import django.contrib.postgres.fields
import video_app.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0002_delete_videoprogress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='available_resolutions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), blank=True, default=list, help_text='list generated automatically', size=None),
        ),
        migrations.AlterField(
            model_name='video',
            name='sprite_sheet',
            field=models.FileField(blank=True, help_text='Sprite sheet generated automatically', null=True, storage=video_app.storage_backends.OverwriteStorage(), upload_to='videos/sprites/'),
        ),
    ]
