from django.apps import AppConfig


class ColorDiaryConfig(AppConfig):
    name = 'color_diary'

    def ready(self):
        from . import signals
