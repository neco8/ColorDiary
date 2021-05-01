from django.test import TestCase
from django.contrib.auth import get_user_model

from ..fields import HexColor
from ..models import Color
from .constant import *
from . import UserModelTests
from ..signals import hex_color_list


class UserPostSaveTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        Color.objects.all().delete()
        User.objects.all().delete()

    def test_default_color_setting_after_user_create(self):
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        transparent = Color.get_default_color().hex_color
        self.assertEqual(user.colors.all().count(), 1 + len(hex_color_list))
        self.assertEqual(user.colors.all().order_by('-hex_color')[0].hex_color, transparent)

    def test_default_color_setting_with_two_users(self):
        user1 = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        user2 = UserModelTests.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        transparent = Color.get_default_color().hex_color
        self.assertEqual(user1.colors.all().count(), 1 + len(hex_color_list))
        self.assertEqual(user2.colors.all().count(), 1 + len(hex_color_list))
        self.assertEqual(user1.colors.all().order_by('-hex_color')[0].hex_color, transparent)
        self.assertEqual(user2.colors.all().order_by('-hex_color')[0].hex_color, transparent)
        self.assertEqual(Color.objects.all().count(), 1 + len(hex_color_list))
        self.assertEqual(Color.objects.filter(users__id=user1.pk).count(), 1 + len(hex_color_list))
        self.assertEqual(Color.objects.filter(users__id=user2.pk).count(), 1 + len(hex_color_list))
