# Standard libraries
import os
import subprocess

# ???
from urllib.parse import urljoin

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


# def finalize_hls(video, base, root, entries, names):
#     """
#     Write master playlist, save file, and update the video record.
#     """
#     master = os.path.join(root, f"{base}.m3u8")
#     write_master_playlist(master, entries)
#     save_file(video, 'hls_playlist', master, f"{base}.m3u8")
#     video.available_resolutions = list(names)
#     video.save(update_fields=['hls_playlist', 'available_resolutions'])

def finalize_hls(video, base, root, entries, names):
    """
    Write master playlist, save file, and update the video record.

    Important:
    - Write the master to disk (root/<base>.m3u8).
    - Save it via the model's FileField using a name *relative* to the field.upload_to
      so Django doesn't duplicate the upload_to path.
    - Keep playlist entries relative (e.g. "720p/index.m3u8") so they resolve correctly.
    """
    master = os.path.join(root, f"{base}.m3u8")

    # Ensure entries contain only relative URIs like "720p/index.m3u8"
    # (build_hls_entry already produces that, but normalize defensively)
    normalized_entries = []
    for e in entries:
        uri = e.get('uri', '')
        # if someone accidentally wrote an absolute/incorrect URI, reduce to "<name>/index.m3u8"
        # attempt to extract the last two path components (resolution/index.m3u8)
        parts = uri.replace('\\', '/').split('/')
        if len(parts) >= 2:
            uri = '/'.join(parts[-2:])
        normalized_entries.append({
            'uri': uri,
            'bandwidth': e['bandwidth'],
            'resolution': e['resolution'],
        })

    write_master_playlist(master, normalized_entries)

    # Save the master into the FileField. Pass a filename *relative* to the field.upload_to
    # so Django's FieldFile.generate_filename doesn't prepend upload_to twice.
    # Using "<base>/<base>.m3u8" places the master next to the "<base>/" subfolders.
    name_for_field = os.path.join(base, f"{base}.m3u8")

    save_file(video, 'hls_playlist', master, name_for_field)

    # update available_resolutions and persist
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


def get_video_duration(path):
    """
    Get video duration in seconds.
    """
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration', '-of',
        'default=noprint_wrappers=1:nokey=1', path
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        return int(float(result.stdout.strip()))
    except Exception:
        return None


def get_resolution_urls(video, request=None):
    """
    Given a Video instance, return a dict mapping resolution name ->
    public playlist URL, e.g.
      { "720p": "http://127.0.0.1:8000/media/videos/hls/<base>/720p/index.m3u8", ... }

    Uses (in order):
      1. request.build_absolute_uri(...) when `request` is provided (recommended).
      2. settings.MEDIA_URL if it contains an absolute URL (starts with http/https).
      3. falls back to a relative path using MEDIA_URL (may return "/media/..." or similar).

    Returns empty dict if there is no hls_playlist or no available_resolutions.
    """
    # prefer the saved hls_playlist field to derive the base name
    playlist_field = getattr(video, 'hls_playlist', None)
    if not playlist_field:
        # fallback to derive base from video_file if available
        source = getattr(video, 'video_file', None)
        if not source:
            return {}
        value = getattr(source, 'name', None)
    else:
        value = getattr(playlist_field, 'name', None)

    if not value:
        return {}

    base = os.path.splitext(os.path.basename(value))[0]

    # build the relative media path (always start with a slash if MEDIA_URL is '/media/')
    media_url = settings.MEDIA_URL or '/'
    # Ensure media_url ends with a slash for joining
    if not media_url.endswith('/'):
        media_url = media_url + '/'

    mapping = {}
    for name in getattr(video, 'available_resolutions', []) or []:
        # Relative portion under MEDIA_URL
        rel_under_media = f"videos/hls/{base}/{name}/index.m3u8"

        # If a request exists, use it to build absolute URI from the relative path
        if request is not None:
            # Build absolute path relative to the site's root
            # If MEDIA_URL is relative like '/media/', prefix it before building absolute.
            if media_url.startswith('http://') or media_url.startswith('https://'):
                # MEDIA_URL already absolute, join to it
                mapping[name] = urljoin(media_url, rel_under_media)
            else:
                # ensure starting slash for build_absolute_uri
                rel_path = media_url.rstrip('/') + '/' + rel_under_media
                mapping[name] = request.build_absolute_uri(rel_path)
            continue

        # No request available: try to use MEDIA_URL if it's absolute
        if media_url.startswith('http://') or media_url.startswith('https://'):
            mapping[name] = urljoin(media_url, rel_under_media)
        else:
            # fallback: return a relative path (e.g. "/media/videos/...")
            mapping[name] = urljoin(media_url, rel_under_media)

    return mapping
