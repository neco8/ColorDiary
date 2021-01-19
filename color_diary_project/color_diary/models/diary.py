from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from . import User, Color


class Diary(models.Model):
    COLOR_LEVELS = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    ]

    user = models.ForeignKey(User, related_name='diaries', related_query_name='diary', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name='diaries', related_query_name='diary', on_delete=models.SET(Color.get_default_color))
    color_level = models.PositiveSmallIntegerField(choices=COLOR_LEVELS, validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    context = models.TextField("diary's context", blank=True)
