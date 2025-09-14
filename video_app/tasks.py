# Standard libraries
import json
import subprocess
from pathlib import Path
from typing import Iterable

# Third-party suppliers
from django.db import transaction

# Local imports
from .models import Video
from .utils import MEDIA_ROOT, ensure_dirs, quality_payload, video_name_from_path


LADDER = [
    ("1920x1080", "5000k", "v0", 6000000),
    ("1280x720", "2800k", "v1", 3500000),
    ("640x360", "800k", "v2", 1200000),
    ("256x144", "200k", "v3", 400000),
]


def _run(cmd: list[str]) -> None:
    """Run a shell command and raise on failure."""
    subprocess.run(cmd, check=True)


def probe_duration(src: Path) -> float:
    """Return media duration in seconds via ffprobe."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(src)
    ])
    data = json.loads(out.decode() or "{}")
    return float(data.get("format", {}).get("duration", 0.0))


def transcode_variant(src: Path, out_dir: Path, size: str, bitrate: str) -> None:
    """Transcode a single HLS variant into out_dir."""
    ensure_dirs([out_dir])
    _run([
        "ffmpeg", "-y", "-i", str(src),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-g", "48", "-s:v", size, "-b:v", bitrate, "-c:a", "aac",
        "-hls_time", "6", "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(out_dir / "seg_%03d.ts"),
        str(out_dir / "index.m3u8"),
    ])


def write_master_playlist(hls_dir: Path, entries: Iterable[tuple[str, int]]) -> None:
    """Write master.m3u8 referencing variant playlists."""
    master = hls_dir / "master.m3u8"
    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]
    for res, bw in entries:
        lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={bw},RESOLUTION={res}")
        lines.append(f"v{len(lines)//2 - 1}/index.m3u8")
    master.write_text("\n".join(lines) + "\n", encoding="utf-8")


def transcode_ladder(src: Path, root: Path) -> None:
    """Create HLS ladder directories and a master playlist."""
    hls = root / "hls"
    ensure_dirs([hls])
    for size, br, folder, _ in LADDER:
        transcode_variant(src, hls / folder, size, br)
    entries = [(size, bw) for size, _, _, bw in LADDER]
    write_master_playlist(hls, entries)


def make_preview(src: Path, root: Path) -> Path:
    """Create a short MP4 preview clip."""
    outp = root / "previews" / "preview.mp4"
    ensure_dirs([outp.parent])
    _run(["ffmpeg", "-y", "-ss", "0", "-t", "10", "-i", str(src),
          "-c:v", "libx264", "-c:a", "aac", str(outp)])
    return outp


def make_thumbnail(src: Path, root: Path) -> Path:
    """Create a JPG thumbnail."""
    outp = root / "thumbs" / "thumb.jpg"
    ensure_dirs([outp.parent])
    _run(["ffmpeg", "-y", "-ss", "5", "-i", str(src),
          "-frames:v", "1", "-q:v", "2", str(outp)])
    return outp


def update_video_record(video: Video, name: str, dur: float) -> None:
    """Persist derived fields for a processed video."""
    video.duration = dur
    video.hls_playlist.name = f"videos/{name}/hls/master.m3u8"
    video.quality_levels = quality_payload(name)
    video.preview.name = f"videos/{name}/previews/preview.mp4"
    video.thumbnail.name = f"videos/{name}/thumbs/thumb.jpg"
    video.save(update_fields=[
        "duration", "hls_playlist", "quality_levels", "preview", "thumbnail"
    ])


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
    make_preview(src, root)
    make_thumbnail(src, root)
    with transaction.atomic():
        update_video_record(video, name, dur)
