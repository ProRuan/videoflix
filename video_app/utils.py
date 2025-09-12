# Standard libraries
import json
import os
import shlex
import subprocess
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Third-party suppliers
from django.conf import settings

# Local imports


def run(cmd: str) -> int:
    """
    Run a shell command safely and return the exit code.
    """
    return subprocess.call(shlex.split(cmd))


def media_path(*parts: str) -> str:
    """
    Build an absolute path inside MEDIA_ROOT.
    """
    return os.path.join(settings.MEDIA_ROOT, *parts)


def ensure_dir(path: str) -> None:
    """
    Ensure directory exists for a path.
    """
    os.makedirs(path, exist_ok=True)


def probe_duration(input_path: str) -> float:
    """
    Read duration in seconds using ffprobe.
    """
    cmd = (
        "ffprobe -v error -show_entries format=duration "
        f"-of default=nk=1:nw=1 {shlex.quote(input_path)}"
    )
    out = subprocess.check_output(cmd, shell=True).decode().strip()
    return float(out) if out else 0.0


def build_hls_out(video_id: int) -> str:
    """
    Return HLS output directory for video id.
    """
    return media_path("videos", "hls", f"v{video_id}")


def quality_map(base_url: str) -> list[dict]:
    """
    Build quality_levels array for the four rungs.
    """
    return [
        {"label": "1080p", "source": f"{base_url}/v0/index.m3u8"},
        {"label": "720p", "source": f"{base_url}/v1/index.m3u8"},
        {"label": "360p", "source": f"{base_url}/v2/index.m3u8"},
        {"label": "120p", "source": f"{base_url}/v3/index.m3u8"},
    ]


def abs_url(request, value: str | object) -> str | None:
    """
    Make an absolute URL from a FileField/relative/absolute value.
    """
    if not value:
        return None
    if hasattr(value, "url"):
        value = value.url
    s = str(value)
    if urlparse(s).scheme:
        return s
    if not s.startswith("/"):
        base = settings.MEDIA_URL.rstrip("/")
        s = f"{base}/{s.lstrip('/')}"
    return request.build_absolute_uri(s)
