# Standard libraries
from django.utils import timezone
from django.db.models import OuterRef, QuerySet, Subquery
from datetime import timedelta
from collections import defaultdict
from typing import Iterable, Sequence
from pathlib import Path
from typing import Iterable

# Third-party suppliers
from django.conf import settings

# Local imports


MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", "media"))
MEDIA_URL = getattr(settings, "MEDIA_URL", "/media/")
HOST = getattr(settings, "BACKEND_HOST", "http://127.0.0.1:8000")


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


# Standard libraries

# Third-party suppliers

# Local imports
# (kept from your previous version)
MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", "media"))
MEDIA_URL = getattr(settings, "MEDIA_URL", "/media/")
HOST = getattr(settings, "BACKEND_HOST", "http://127.0.0.1:8000")


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


# ---------- API helpers (new) ----------

def new_cutoff() -> timezone.datetime:
    """Return cutoff datetime for 'new' videos."""
    days = getattr(settings, "VIDEO_NEW_DAYS", 90)
    return timezone.now() - timedelta(days=days)


def annotate_with_progress(qs: QuerySet, user_id: int):
    """Annotate qs with progress_id/relative_position for a user."""
    from video_progress_app.models import VideoProgress as VP  # lazy import
    vp = VP.objects.filter(user_id=user_id, video_id=OuterRef("pk"))
    return qs.annotate(
        progress_id=Subquery(vp.values("id")[:1]),
        relative_position=Subquery(vp.values("relative_position")[:1]),
    )


def annotate_detail_with_progress(qs: QuerySet, user_id: int):
    """Annotate qs with progress_id/last_position for a user."""
    from video_progress_app.models import VideoProgress as VP  # lazy import
    vp = VP.objects.filter(user_id=user_id, video_id=OuterRef("pk"))
    return qs.annotate(
        progress_id=Subquery(vp.values("id")[:1]),
        last_position=Subquery(vp.values("last_position")[:1]),
    )


def group_by_genre(videos: Sequence) -> dict[str, list]:
    """Group videos by their genre."""
    grouped: dict[str, list] = defaultdict(list)
    for v in videos:
        grouped[v.genre].append(v)
    return grouped


def serialize_items(items, request):
    """Serialize list items with the list serializer."""
    from .api.serializers import VideoListItemSerializer as S
    return S(items, many=True, context={"request": request}).data


def append_section(payload: list, title: str, items: Sequence, request) -> None:
    """Append a section if it has items."""
    if items:
        payload.append(
            {"genre": title, "videos": serialize_items(items, request)})


def build_list_payload(videos: Sequence, request) -> list[dict]:
    """Build list payload (new, started, genres)."""
    payload: list[dict] = []
    cutoff = new_cutoff()
    new_items = [v for v in videos if v.created_at >= cutoff]
    started = [v for v in videos if getattr(
        v, "progress_id", None) is not None]
    append_section(payload, "New on Videoflix", new_items, request)
    append_section(payload, "Started videos", started, request)
    for genre, items in sorted(group_by_genre(videos).items()):
        append_section(payload, genre, items, request)
    return payload
