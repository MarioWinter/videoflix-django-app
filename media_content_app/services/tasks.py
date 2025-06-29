import os
import subprocess
from tempfile import NamedTemporaryFile
from django.core.files import File
from django.conf import settings
from media_content_app.models import Video

def run_ffmpeg(command):
    command.insert(1, '-y')  # wichtig: -y direkt hinter 'ffmpeg' damit falls vorhandene gelöscht werden  
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("FFMPEG STDERR:", result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print("FFMPEG ERROR:", e.stderr.decode())
        raise

def generate_thumbnail_and_resolutions(video_id):
    video = Video.objects.get(id=video_id)
    original_path = video.video_file.path

    resolutions = {
        'video_1080p': '1920x1080',
        'video_720p': '1280x720',
        'video_360p': '640x360',
        'video_120p': '160x120',
    }

    for field, res in resolutions.items():
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

        ext = os.path.splitext(original_path)[1]  # z. B. ".mp4"
        filename = f'{field}_{video_id}{ext}' 

        with open(temp_path, 'rb') as f:
            getattr(video, field).save(filename, File(f), save=False)

        os.remove(temp_path)

    # thumbnail generieren / name muss noch vom video übernommen werden
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
    with open(thumb_path, 'rb') as f:
        video.thumbnail.save(f'thumbnail_{video_id}.jpg', File(f), save=False)

    os.remove(thumb_path)
    video.save()
    print("Thumbnail Pfad:", video.thumbnail.path, os.path.exists(video.thumbnail.path))
    for field in ['video_1080p', 'video_720p', 'video_360p', 'video_120p']:
        file_field = getattr(video, field)
        print(f"{field} Pfad:", file_field.path)