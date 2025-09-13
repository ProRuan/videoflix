# Standard libraries
import os
from pathlib import Path
from typing import Iterable

# Third-party suppliers
from django.conf import settings

# Local imports


MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", "media"))
MEDIA_URL = getattr(settings, "MEDIA_URL", "/media/")
HOST = "http://127.0.0.1:8000"


def base_media_url() -> str:
    """Return absolute media base."""
    return f"{HOST.rstrip('/')}{MEDIA_URL.rstrip('/')}"


def video_name_from_path(path: str) -> str:
    """Derive a folder name from the original file name without suffix."""
    stem = Path(path).stem
    return stem.replace(" ", "_").lower()


def ensure_dirs(paths: Iterable[Path]) -> None:
    """Create required directories if missing."""
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def absolute_url(rel: str) -> str:
    """Map 'videos/foo/bar' to absolute media url."""
    return f"{base_media_url().rstrip('/')}/{rel.lstrip('/')}"


def quality_payload(name: str) -> list[dict]:
    """Return quality levels payload for API."""
    base = f"videos/{name}/hls"
    labels = ["1080p", "720p", "360p", "144p"]
    return [
        {"label": labels[i], "source": absolute_url(f"{base}/v{i}/index.m3u8")}
        for i in range(4)
    ]
