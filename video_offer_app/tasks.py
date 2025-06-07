import subprocess

# remove first mp4 in path!


def convert_480p(source):
    target = source + '480p_mp4'
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(
        source, target)
    subprocess.run(cmd)
