from rest_framework import serializers
from media_content_app.models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'genre', 'description', 'thumbnail', 'uploaded_at', 'video_1080p', 'video_720p', 'video_360p', 'video_120p']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            if instance.thumbnail:
                rep['thumbnail'] = request.build_absolute_uri(instance.thumbnail.url)
            if instance.video_1080p:
                rep['video_1080p'] = request.build_absolute_uri(instance.video_1080p.url)
            if instance.video_720p:
                rep['video_720p'] = request.build_absolute_uri(instance.video_720p.url)
            if instance.video_360p:
                rep['video_360p'] = request.build_absolute_uri(instance.video_360p.url)
            if instance.video_120p:
                rep['video_120p'] = request.build_absolute_uri(instance.video_120p.url)
        return rep

