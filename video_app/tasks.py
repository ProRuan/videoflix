# Standard libraries
import os

# Local imports
from .utils import (
    ensure_dir, finalize_hls, get_hls_paths,
    get_video, media_path, process_resolution,
    run_cmd, save_file,
)

RESOLUTIONS = [
    {'name': '1080p', 'width': 1920, 'height': 1080,
        'v_bitrate': '5000k', 'a_bitrate': '192k'},
    {'name': '720p',  'width': 1280, 'height': 720,
        'v_bitrate': '2800k', 'a_bitrate': '128k'},
    {'name': '360p',  'width':  640, 'height': 360,
        'v_bitrate': '800k',  'a_bitrate': '96k'},
    {'name': '120p',  'width':  160, 'height': 120,
        'v_bitrate': '200k',  'a_bitrate': '64k'},
]


def generate_hls(video_id):
    """
    Generate HLS streams for all resolutions and update Video.
    """
    vid = get_video(video_id)
    source, base, root = get_hls_paths(vid)
    results = [process_resolution(source, root, r) for r in RESOLUTIONS]
    names, entries = zip(*results)
    finalize_hls(vid, base, root, entries, names)


def generate_preview(video_id, duration=10):
    """
    Generate preview clip and update Video.
    """
    vid = get_video(video_id)
    src = vid.video_file.path
    base = os.path.splitext(os.path.basename(src))[0]
    tgt = media_path('videos', 'preview', f"{base}_preview.mp4")
    ensure_dir(os.path.dirname(tgt))
    cmd = ['ffmpeg', '-i', src, '-ss', '00:00:00', '-t', str(duration),
           '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', tgt]
    run_cmd(cmd)
    save_file(vid, 'preview_clip', tgt, os.path.basename(tgt))


def generate_thumbnail(video_id, timestamp='00:00:03'):
    """
    Generate thumbnail image and update Video.
    """
    vid = get_video(video_id)
    src = vid.video_file.path
    base = os.path.splitext(os.path.basename(src))[0]
    tgt = media_path('videos', 'thumbs', f"{base}_thumb.jpg")
    ensure_dir(os.path.dirname(tgt))
    cmd = ['ffmpeg', '-i', src, '-ss', timestamp, '-vframes', '1',
           '-s', '320x180', '-q:v', '2', tgt]
    run_cmd(cmd)
    save_file(vid, 'thumbnail_image', tgt, os.path.basename(tgt))


def generate_sprite_sheet(video_id, interval=10, columns=5):
    """
    Generate sprite sheet and update Video.
    """
    vid = get_video(video_id)
    src = vid.video_file.path
    base = os.path.splitext(os.path.basename(src))[0]
    sheet_dir = media_path('videos', 'sprites')
    ensure_dir(sheet_dir)
    rows = max(1, ((vid.duration or 0) // interval + columns - 1) // columns)
    vf = f"fps=1/{interval},scale=320:-1,tile={columns}x{rows}"
    tgt = media_path(sheet_dir, f"{base}_sprite.jpg")
    cmd = ['ffmpeg', '-i', src, '-vf', vf, '-q:v', '2', '-frames:v', '1', tgt]
    run_cmd(cmd)
    save_file(vid, 'sprite_sheet', tgt, os.path.basename(tgt))
