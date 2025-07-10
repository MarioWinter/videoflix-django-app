import os
import subprocess
from tempfile import NamedTemporaryFile
from django.core.files import File
from media_content_app.models import Video

def run_ffmpeg(command):
    command.insert(1, '-y')
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def generate_thumbnail_and_resolutions(video_id):
    video = Video.objects.get(id=video_id)
    original_path = video.video_file.path
    base_name = os.path.splitext(os.path.basename(original_path))[0]

    resolutions = {
        'video_1080p': ('1920x1080', '1080p'),
        'video_720p': ('1280x720', '720p'),
        'video_360p': ('640x360', '360p'),
        'video_120p': ('160x120', '120p'),
    }

    for field, (res, suffix) in resolutions.items():
        temp = NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_path = temp.name
        command = [
            'ffmpeg',
            '-i', original_path,
            '-s', res,
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'veryfast',
            '-c:a', 'aac',
            '-strict', '-2',
            temp_path
        ]
        run_ffmpeg(command)
        filename = f'{base_name}_{suffix}.mp4'
        with open(temp_path, 'rb') as f:
            getattr(video, field).save(filename, File(f), save=False)
        os.remove(temp_path)

    # Thumbnail nur einmal erzeugen
    thumb_temp = NamedTemporaryFile(suffix='.jpg', delete=False)
    thumb_path = thumb_temp.name
    command = [
        'ffmpeg',
        '-i', original_path,
        '-ss', '00:00:01.000',
        '-vframes', '1',
        thumb_path
    ]
    run_ffmpeg(command)

    thumb_filename = f'{base_name}.jpg'
    with open(thumb_path, 'rb') as f:
        video.thumbnail.save(thumb_filename, File(f), save=False)
    os.remove(thumb_path)

    video.save()  