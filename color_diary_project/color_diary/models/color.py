from django.db import models
from django.contrib.auth import get_user_model

from ..fields import HexColor, HexColorField


class ColorManager(models.Manager):
    def create(self, hex_color):
        # Eliminate duplicates.
        try:
            Color.objects.get(hex_color=hex_color)
        except Color.DoesNotExist:
            color = super().create(hex_color=hex_color)
            return color
        else:
            color = Color.objects.get(hex_color=hex_color)
            return color


class Color(models.Model):
    # todo: 設定としてデフォルト色ファイルとかも作ってみたい
    User = get_user_model()
    users = models.ManyToManyField(User, related_name='colors', related_query_name='color')
    hex_color = HexColorField(verbose_name='hex color code')
    objects = ColorManager()

    class Meta:
        ordering = ['-hex_color', 'id']

    @classmethod
    def get_default_color(cls):
        transparent = HexColor('FF', 'FF', 'FF', 0.0)
        default_color = cls.objects.create(hex_color=transparent)
        return default_color

    def __str__(self):
        return str(self.hex_color)
