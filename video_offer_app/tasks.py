import os
import subprocess
from django.core.files import File
from django.conf import settings
from .models import Video


def _run(cmd):
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg error:", e)
        raise


def generate_hls(instance_id):
    """
    For a given Video PK, produce 1080p, 720p, 360p, 120p HLS streams,
    plus a master playlist.
    """
    vid = Video.objects.get(id=instance_id)
    source = vid.video_file.path
    base = os.path.splitext(os.path.basename(source))[0]

    # where to write HLS files
    hls_root = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', base)
    os.makedirs(hls_root, exist_ok=True)

    # Define your renditions
    renditions = [
        {'name': '1080p', 'width': 1920, 'height': 1080,
            'v_bitrate': '5000k', 'a_bitrate': '192k'},
        {'name': '720p',  'width': 1280, 'height': 720,
            'v_bitrate': '2800k', 'a_bitrate': '128k'},
        {'name': '360p',  'width':  640, 'height': 360,
            'v_bitrate': '800k',  'a_bitrate': '96k'},
        {'name': '120p',  'width':  160, 'height': 120,
            'v_bitrate': '200k',  'a_bitrate': '64k'},
    ]

    playlist_entries = []

    for r in renditions:
        # create folder for each variant
        out_dir = os.path.join(hls_root, r['name'])
        os.makedirs(out_dir, exist_ok=True)

        segment_pattern = os.path.join(out_dir, 'seg_%03d.ts')
        playlist_file = os.path.join(out_dir, 'index.m3u8')

        cmd = [
            'ffmpeg', '-i', source,
            '-vf', f"scale=w={r['width']}:h={r['height']}",
            '-c:v', 'libx264', '-b:v', r['v_bitrate'], '-preset', 'fast',
            '-c:a', 'aac',    '-b:a', r['a_bitrate'],
            '-hls_time', '10',
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', segment_pattern,
            playlist_file
        ]
        _run(cmd)

        # store for master playlist
        bandwidth = int(r['v_bitrate'].rstrip('k')) * 1000
        playlist_entries.append({
            'uri': f"{r['name']}/index.m3u8",
            'bandwidth': bandwidth,
            'resolution': f"{r['width']}x{r['height']}"
        })

    # build master playlist
    master_path = os.path.join(hls_root, f"{base}.m3u8")
    with open(master_path, 'w') as m:
        m.write('#EXTM3U\n')
        for e in playlist_entries:
            m.write(
                f"#EXT-X-STREAM-INF:BANDWIDTH={e['bandwidth']},RESOLUTION={e['resolution']}\n")
            m.write(f"{e['uri']}\n")

    # save to model
    with open(master_path, 'rb') as f:
        vid.hls_playlist.save(f"{base}.m3u8", File(f), save=True)


# def generate_hls(instance_id):
#     vid = Video.objects.get(id=instance_id)
#     source = vid.video_file.path
#     base = os.path.splitext(os.path.basename(source))[0]
#     hls_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', base)
#     os.makedirs(hls_dir, exist_ok=True)

#     # Build FFmpeg cmd: 4 renditions
#     cmd = [
#         'ffmpeg', '-i', source,
#         # 1080p
#         '-vf', "scale=w=1920:h=1080", '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
#         '-c:a', 'aac', '-b:a', '128k',
#         '-f', 'hls', '-hls_time', '10', '-hls_list_size', '0',
#         os.path.join(hls_dir, f'{base}_1080p.m3u8')
#     ]
#     _run(cmd)
#     # You can repeat or (better) use a single ffmpeg call with -var_stream_map etc.

#     # Save master playlist file back to model
#     playlist_path = os.path.join(hls_dir, f'{base}_1080p.m3u8')
#     with open(playlist_path, 'rb') as f:
#         vid.hls_playlist.save(f'{base}.m3u8', File(f), save=True)


def generate_preview(instance_id, duration=10):
    vid = Video.objects.get(id=instance_id)
    source = vid.video_file.path
    base = os.path.splitext(os.path.basename(source))[0]
    target = os.path.join(settings.MEDIA_ROOT,
                          'videos/preview/', base + '_preview.mp4')
    os.makedirs(os.path.dirname(target), exist_ok=True)

    cmd = [
        'ffmpeg', '-i', source,
        '-ss', '00:00:00',
        '-t', str(duration),
        '-c:v', 'libx264', '-crf', '23',
        '-c:a', 'aac',
        target
    ]
    _run(cmd)
    with open(target, 'rb') as f:
        vid.preview_clip.save(os.path.basename(target), File(f), save=True)


def generate_thumbnail(instance_id, timestamp='00:00:03'):
    vid = Video.objects.get(id=instance_id)
    source = vid.video_file.path
    base = os.path.splitext(os.path.basename(source))[0]
    target = os.path.join(settings.MEDIA_ROOT,
                          'videos/thumbs/', base + '_thumb.jpg')
    os.makedirs(os.path.dirname(target), exist_ok=True)

    cmd = [
        'ffmpeg', '-i', source,
        '-ss', timestamp,
        '-vframes', '1',
        '-s', '320x180',
        '-q:v', '2',
        target
    ]
    _run(cmd)
    with open(target, 'rb') as f:
        vid.thumbnail_image.save(os.path.basename(target), File(f), save=True)


def generate_sprite_sheet(instance_id, interval=10, columns=5):
    """
    Generate a contact sheet (sprite) image for the video.
    interval: seconds between thumbnails
    columns: number of columns in the sprite grid
    """
    vid = Video.objects.get(id=instance_id)
    source = vid.video_file.path
    base = os.path.splitext(os.path.basename(source))[0]
    sprite_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'sprites')
    os.makedirs(sprite_dir, exist_ok=True)
    sprite_path = os.path.join(sprite_dir, f"{base}_sprite.jpg")

    # use ffmpeg to generate tiled sprite
    # -vf fps=1/interval,scale=320:-1,tile=columnsxrows
    # First compute rows based on duration
    duration = vid.duration or 0
    rows = max(1, (duration // interval + columns - 1) // columns)
    vf = f"fps=1/{interval},scale=320:-1,tile={columns}x{rows}"
    cmd = [
        'ffmpeg', '-i', source,
        '-vf', vf,
        '-q:v', '2',
        '-frames:v', '1',
        sprite_path
    ]
    _run(cmd)

    with open(sprite_path, 'rb') as f:
        vid.sprite_sheet.save(os.path.basename(
            sprite_path), File(f), save=True)
