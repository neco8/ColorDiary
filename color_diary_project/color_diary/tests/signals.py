from django.test import TestCase
from django.contrib.auth import get_user_model

from ..fields import HexColor
from ..models import Color
from .constant import *
from . import UserModelTests


class UserPostSaveTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        Color.objects.all().delete()
        User.objects.all().delete()

    def test_default_color_setting_after_user_create(self):
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        transparent = HexColor('ff', 'ff', 'ff', 0.0)
        self.assertEqual(user.colors.all().count(), 1)
        self.assertEqual(user.colors.all()[0].hex_color, transparent)

    def test_default_color_setting_with_two_users(self):
        user1 = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        user2 = UserModelTests.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        transparent = HexColor('ff', 'ff', 'ff', 0.0)
        self.assertEqual(user1.colors.all().count(), 1)
        self.assertEqual(user2.colors.all().count(), 1)
        self.assertEqual(user1.colors.all()[0].hex_color, transparent)
        self.assertEqual(user2.colors.all()[0].hex_color, transparent)
        self.assertEqual(Color.objects.all().count(), 1)
        self.assertEqual(Color.objects.filter(users__id=user1.pk).count(), 1)
        self.assertEqual(Color.objects.filter(users__id=user2.pk).count(), 1)
