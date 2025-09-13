# Standard libraries
import json
import subprocess
from pathlib import Path

# Third-party suppliers
from django.db import transaction

# Local imports
from .models import Video
from .utils import (MEDIA_ROOT, absolute_url, ensure_dirs, quality_payload,
                    video_name_from_path)


def _run(cmd: list[str]) -> None:
    """Run a shell command and raise on failure."""
    subprocess.run(cmd, check=True)


def probe_duration(src: Path) -> float:
    """Return media duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(src)
    ]
    out = subprocess.check_output(cmd)
    data = json.loads(out.decode() or "{}")
    return float(data.get("format", {}).get("duration", 0.0))


def transcode_ladder(src: Path, root: Path) -> None:
    """Create HLS ladder (v0..v3) and master playlist."""
    hls = root / "hls"
    ensure_dirs([hls])
    maps = [
        ("1920x1080", "5000k", "v0"),
        ("1280x720", "2800k", "v1"),
        ("640x360", "800k", "v2"),
        ("256x144", "200k", "v3"),
    ]
    for size, br, folder in maps:
        out_dir = hls / folder
        ensure_dirs([out_dir])
        _run([
            "ffmpeg", "-y", "-i", str(src),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-g", "48", "-s:v", size, "-b:v", br, "-c:a", "aac",
            "-hls_time", "6", "-hls_playlist_type", "vod",
            "-hls_segment_filename", str(out_dir / "seg_%03d.ts"),
            str(out_dir / "index.m3u8")
        ])
    master = hls / "master.m3u8"
    with master.open("w", encoding="utf-8") as f:
        f.write("#EXTM3U\n#EXT-X-VERSION:3\n")
        f.write('#EXT-X-STREAM-INF:BANDWIDTH=6000000,RESOLUTION=1920x1080\n')
        f.write("v0/index.m3u8\n")
        f.write('#EXT-X-STREAM-INF:BANDWIDTH=3500000,RESOLUTION=1280x720\n')
        f.write("v1/index.m3u8\n")
        f.write('#EXT-X-STREAM-INF:BANDWIDTH=1200000,RESOLUTION=640x360\n')
        f.write("v2/index.m3u8\n")
        f.write('#EXT-X-STREAM-INF:BANDWIDTH=400000,RESOLUTION=256x144\n')
        f.write("v3/index.m3u8\n")


def make_preview(src: Path, root: Path) -> Path:
    """Create a short MP4 preview clip."""
    prev_dir = root / "previews"
    ensure_dirs([prev_dir])
    outp = prev_dir / "preview.mp4"
    _run(["ffmpeg", "-y", "-ss", "0", "-t", "10", "-i", str(src),
          "-c:v", "libx264", "-c:a", "aac", str(outp)])
    return outp


def make_thumbnail(src: Path, root: Path) -> Path:
    """Create a JPG thumbnail."""
    img_dir = root / "thumbs"
    ensure_dirs([img_dir])
    outp = img_dir / "thumb.jpg"
    _run(["ffmpeg", "-y", "-ss", "5", "-i", str(src),
          "-frames:v", "1", "-q:v", "2", str(outp)])
    return outp


def process_video(video_id: int) -> None:
    """Orchestrate processing and update model fields."""
    video = Video.objects.get(id=video_id)
    if not video.video_file:
        return
    src = MEDIA_ROOT / str(video.video_file)
    name = video_name_from_path(src.name)
    root = MEDIA_ROOT / "videos" / name
    ensure_dirs([root])
    dur = probe_duration(src)
    transcode_ladder(src, root)
    prev = make_preview(src, root)
    thumb = make_thumbnail(src, root)
    master_rel = f"videos/{name}/hls/master.m3u8"
    with transaction.atomic():
        video.duration = dur
        video.hls_playlist.name = master_rel
        video.quality_levels = quality_payload(name)
        video.preview.name = f"videos/{name}/previews/preview.mp4"
        video.thumbnail.name = f"videos/{name}/thumbs/thumb.jpg"
        video.save(update_fields=[
            "duration", "hls_playlist", "quality_levels",
            "preview", "thumbnail"
        ])
