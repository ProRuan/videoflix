# Standard libraries
import os
import subprocess

# Third-party suppliers
from django.conf import settings
from django.core.files import File

# Local imports
from .models import Video


def run_cmd(cmd):
    """
    Run a shell command.
    """
    subprocess.run(cmd, check=True)


def get_video(video_id):
    """
    Get a video instance by ID.
    """
    return Video.objects.get(pk=video_id)


def ensure_dir(path):
    """
    Create a directory if it does not exist.
    """
    os.makedirs(path, exist_ok=True)


def media_path(*parts):
    """
    Build an absolute path under MEDIA_ROOT.
    """
    return os.path.join(settings.MEDIA_ROOT, *parts)


def save_file(instance, field_name, file_path, filename):
    """
    Save a local file to a FileField.
    """
    with open(file_path, 'rb') as f:
        getattr(instance, field_name).save(filename, File(f), save=True)


def process_resolution(source, root, resolution):
    """
    Transcode a resolution and return its name and playlist entry.
    """
    name = resolution['name']
    out_dir = os.path.join(root, name)
    ensure_dir(out_dir)
    cmd = build_hls_cmd(source, out_dir, resolution)
    run_cmd(cmd)
    entry = build_hls_entry(name, resolution)
    return name, entry


def build_hls_cmd(source, out_dir, resolution):
    """
    Construct ffmpeg command for HLS segmenting.
    """
    seg = os.path.join(out_dir, 'seg_%03d.ts')
    plist = os.path.join(out_dir, 'index.m3u8')
    return [
        'ffmpeg', '-i', source,
        '-vf', f"scale={resolution['width']}:{resolution['height']}",
        '-c:v', 'libx264', '-b:v', resolution['v_bitrate'], '-preset', 'fast',
        '-c:a', 'aac', '-b:a', resolution['a_bitrate'],
        '-hls_time', '10', '-hls_playlist_type', 'vod',
        '-hls_segment_filename', seg, plist
    ]


def build_hls_entry(name, resolution):
    """
    Build master playlist entry metadata.
    """
    bw = int(resolution['v_bitrate'].rstrip('k')) * 1000
    return {
        'uri': f"{name}/index.m3u8",
        'bandwidth': bw,
        'resolution': f"{resolution['width']}x{resolution['height']}"
    }


def get_hls_paths(video):
    """
    Compute source, base name, and output root for HLS.
    """
    source = video.video_file.path
    base = os.path.splitext(os.path.basename(source))[0]
    root = media_path('videos', 'hls', base)
    ensure_dir(root)
    return source, base, root


def finalize_hls(video, base, root, entries, names):
    """
    Write master playlist, save file, and update the video record.
    """
    master = os.path.join(root, f"{base}.m3u8")
    write_master_playlist(master, entries)
    save_file(video, 'hls_playlist', master, f"{base}.m3u8")
    video.available_resolutions = list(names)
    video.save(update_fields=['hls_playlist', 'available_resolutions'])


def write_master_playlist(master_path, entries):
    """
    Write HLS master playlist given entries.
    """
    with open(master_path, 'w') as m:
        m.write('#EXTM3U\n')
        for e in entries:
            m.write(f"#EXT-X-STREAM-INF:BANDWIDTH={e['bandwidth']}"
                    f",RESOLUTION={e['resolution']}\n")
            m.write(f"{e['uri']}\n")
