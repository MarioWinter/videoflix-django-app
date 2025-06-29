from django.apps import AppConfig


class MediaContentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media_content_app'

    # ready funktion erbst von der appconfig
    def ready(self):
        from . import signals
        # import media_content_app.signals