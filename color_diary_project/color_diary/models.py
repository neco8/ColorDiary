from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from .fields import HexColorField, HexColor


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError(_('Users must have an email address.'))

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


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
    users = models.ManyToManyField(User, related_name='colors', related_query_name='color')
    hex_color = HexColorField(verbose_name='hex color code')
    objects = ColorManager()

    @classmethod
    def get_default_color(cls):
        transparent = HexColor('FF', 'FF', 'FF', 0.0)
        default_color = cls.objects.create(hex_color=transparent)
        return default_color

    def __str__(self):
        return str(self.hex_color)


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