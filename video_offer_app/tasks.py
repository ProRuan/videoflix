import subprocess
import os


def convert_480p(source):
    # Remove extension and add _480p.mp4
    base, _ = os.path.splitext(source)
    target = base + '_480p.mp4'

    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', 'hd480',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")


def convert_120p(source):
    # Remove extension and add _120p.mp4
    base, _ = os.path.splitext(source)
    target = base + '_120p.mp4'

    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', '160x120',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")


def convert_360p(source):
    # Remove extension and add _360p.mp4
    base, _ = os.path.splitext(source)
    target = base + '_360p.mp4'

    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', '640x360',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")


def convert_720p(source):
    # Remove extension and add _720p.mp4
    base, _ = os.path.splitext(source)
    target = base + '_720p.mp4'

    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', 'hd720',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")


def convert_1080p(source):
    # Remove extension and add _1080p.mp4
    base, _ = os.path.splitext(source)
    target = base + '_1080p.mp4'

    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', 'hd1080',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")


def generate_thumbnail(source):
    # Remove extension and add _thumbnail.jpg
    base, _ = os.path.splitext(source)
    target = base + '_thumbnail.jpg'

    cmd = [
        'ffmpeg',
        '-i', source,
        '-ss', '00:00:03',       # Timestamp for the thumbnail (3 seconds)
        '-vframes', '1',         # Only 1 frame
        '-s', '320x180',         # Resize to 320x180
        '-q:v', '2',             # Quality (lower is better)
        target
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg thumbnail generation failed: {e}")
