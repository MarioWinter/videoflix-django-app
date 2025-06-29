from django.contrib import admin
from .models import Video
from .services.tasks import generate_thumbnail_and_resolutions
import django_rq


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ('video_1080p', 'video_720p', 'video_360p', 'video_120p')
    fields = ('title', 'video_file', 'description', 'thumbnail', 'genre')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'thumbnail' in form.base_fields:
            form.base_fields['thumbnail'].required = False
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
        django_rq.enqueue(generate_thumbnail_and_resolutions, obj.id)
