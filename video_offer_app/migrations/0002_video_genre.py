# Generated by Django 5.1.4 on 2025-06-19 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_offer_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='genre',
            field=models.CharField(default='', max_length=80),
        ),
    ]
