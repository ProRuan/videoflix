# Standard libraries
import os

# Third-party suppliers
from django.conf import settings

# Local imports
from .models import Video
from .utils import (
    ensure_dir, probe_duration, build_hls_out, quality_map, run, media_path,
)


def make_hls(video_id: int) -> None:
    """
    Create CMAF HLS ladder, preview, thumbnail and fill model fields.
    """
    video = Video.objects.get(id=video_id)
    src = video.video_file.path
    outdir = build_hls_out(video_id)
    ensure_dir(outdir)
    seg = 6
    cmd = (
        "ffmpeg -y -i {src} -filter_complex "
        "\"[0:v]split=4[v1080][v720][v360][v120];"
        "[v1080]scale=-2:1080:flags=lanczos[v0];"
        "[v720]scale=-2:720:flags=lanczos[v1];"
        "[v360]scale=-2:360:flags=lanczos[v2];"
        "[v120]scale=-2:120:flags=lanczos[v3]\" "
        "-map [v0] -map a:0? -c:v:0 libx264 -b:v:0 5000k -maxrate:v:0 5350k "
        "-bufsize:v:0 10000k -g:v:0 60 -sc_threshold:v:0 0 "
        "-force_key_frames:v:0 expr:gte(t,n_forced*2) "
        "-map [v1] -map a:0? -c:v:1 libx264 -b:v:1 2800k -maxrate:v:1 3000k "
        "-bufsize:v:1 6000k -g:v:1 60 -sc_threshold:v:1 0 "
        "-force_key_frames:v:1 expr:gte(t,n_forced*2) "
        "-map [v2] -map a:0? -c:v:2 libx264 -b:v:2 800k -maxrate:v:2 900k "
        "-bufsize:v:2 1600k -g:v:2 60 -sc_threshold:v:2 0 "
        "-force_key_frames:v:2 expr:gte(t,n_forced*2) "
        "-map [v3] -map a:0? -c:v:3 libx264 -b:v:3 200k -maxrate:v:3 220k "
        "-bufsize:v:3 400k -g:v:3 60 -sc_threshold:v:3 0 "
        "-force_key_frames:v:3 expr:gte(t,n_forced*2) "
        "-c:a aac -ac 2 -ar 48000 -b:a 128k "
        f"-f hls -hls_time {seg} -hls_playlist_type vod "
        "-hls_flags independent_segments -hls_segment_type fmp4 "
        "-master_pl_name master.m3u8 "
        "-var_stream_map \"v:0,a:0 v:1,a:0 v:2,a:0 v:3,a:0\" "
        f"-hls_segment_filename {outdir}/v%v/seg_%03d.m4s "
        f"{outdir}/v%v/index.m3u8"
    ).format(src=shlex_quote(src))
    run(cmd)
    make_derivatives(video, outdir)


def make_derivatives(video: Video, outdir: str) -> None:
    """
    Create preview and thumbnail, update model with URLs and duration.
    """
    prev = media_path("videos", "previews", f"v{video.id}.mp4")
    thumb = media_path("videos", "thumbs", f"v{video.id}.jpg")
    ensure_dir(os.path.dirname(prev))
    ensure_dir(os.path.dirname(thumb))
    run(f"ffmpeg -y -ss 3 -t 10 -i {shlex_quote(video.video_file.path)} "
        "-c:v libx264 -preset veryfast -crf 22 -c:a aac -b:a 128k "
        "-movflags +faststart {shlex_quote(prev)}")
    run(f"ffmpeg -y -ss 5 -i {shlex_quote(video.video_file.path)} "
        "-frames:v 1 -q:v 2 -vf scale=1280:-2:flags=lanczos "
        f"{shlex_quote(thumb)}")
    update_video_fields(video, outdir, prev, thumb)


def update_video_fields(video: Video, outdir: str,
                        prev: str, thumb: str) -> None:
    """
    Save derived paths, quality map and duration on the model.
    """
    base = settings.MEDIA_URL.rstrip("/") + "/videos/hls/" + f"v{video.id}"
    video.hls_playlist.name = f"videos/hls/v{video.id}/master.m3u8"
    video.quality_levels = quality_map(base)
    video.preview.name = os.path.relpath(prev, settings.MEDIA_ROOT)
    video.thumbnail.name = os.path.relpath(thumb, settings.MEDIA_ROOT)
    video.duration = probe_duration(video.video_file.path)
    video.save()


def shlex_quote(s: str) -> str:
    """
    Local tiny wrapper to avoid importing shlex in many places.
    """
    import shlex
    return shlex.quote(s)
