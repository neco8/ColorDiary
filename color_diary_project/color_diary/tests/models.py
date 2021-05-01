import time
import datetime
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from ..fields import HexColor
from ..models import Color, Diary
from .constant import *
from ..signals import hex_color_list


class UserModelTests(TestCase):
    @classmethod
    def create_user(cls, email, password):
        user = get_user_model().objects.create_user(email=email, password=password)
        return user

    @classmethod
    def create_superuser(cls, email, password):
        superuser = get_user_model().objects.create_superuser(email=email, password=password)
        return superuser

    def assertUser(self, user, email, password, is_staff, is_active):
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.is_staff, is_staff)
        self.assertEqual(user.is_active, is_active)

    def test_user(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        self.assertUser(user, EXAMPLE_EMAIL, PASSWORD1, False, True)

    def test_superuser(self):
        superuser = self.create_superuser(EXAMPLE_EMAIL, PASSWORD1)
        self.assertUser(superuser, EXAMPLE_EMAIL, PASSWORD1, True, True)

    def test_str_of_user(self):
        self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        user = get_user_model().objects.get(email=EXAMPLE_EMAIL)
        user_string = str(user)
        self.assertEqual(user_string, EXAMPLE_EMAIL)

    def test_filter_by_right_email(self):
        self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        user_queryset = get_user_model().objects.filter(email=EXAMPLE_EMAIL)
        self.assertQuerysetEqual(user_queryset, [f'<User: {EXAMPLE_EMAIL}>'])

    def test_filter_by_wrong_email(self):
        self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        user_queryset = get_user_model().objects.filter(email=EXAMPLE_EMAIL2)
        self.assertQuerysetEqual(user_queryset, [])

    def test_duplicate_email(self):
        with self.assertRaises(IntegrityError):
            self.create_user(EXAMPLE_EMAIL, PASSWORD1)
            self.create_user(EXAMPLE_EMAIL, PASSWORD2)


class ColorModelTests(TestCase):
    @classmethod
    def create_color(cls, red, green, blue, alpha=1.0):
        hex_color = HexColor(red=red, green=green, blue=blue, alpha=alpha)
        color = Color.objects.create(hex_color=hex_color)
        return color

    def assertColor(self, color, red, green, blue, alpha):
        self.assertEqual(color.hex_color.red, red)
        self.assertEqual(color.hex_color.green, green)
        self.assertEqual(color.hex_color.blue, blue)
        self.assertEqual(color.hex_color.alpha, alpha)

    def test_get_default_color(self):
        transparent = Color.get_default_color()
        self.assertColor(transparent, 'FF', 'FF', 'FF', 0.0)

    def test_create_color(self):
        color = self.create_color(red='ff', green='00', blue='00')
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        color.users.add(user)

        hex_color = HexColor('ff', '00', '00')
        get_color = Color.objects.get(hex_color=hex_color)
        self.assertColor(get_color, 'FF', '00', '00', 1.0)

    def test_create_two_colors_with_same_hex_color(self):
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        color1 = self.create_color(red='ff', green='00', blue='00')
        color2 = self.create_color(red='ff', green='00', blue='00')
        color1.users.add(user)
        color2.users.add(user)

        color_list = Color.objects.filter(hex_color=color1.hex_color)
        self.assertEqual(color_list.count(), 1)

    def test_two_users_have_one_color_and_default_colors(self):
        user1 = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        user2 = UserModelTests.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        color = self.create_color(red='ff', green='00', blue='00')
        color.users.add(user1, user2)

        user_list = color.users.all()
        user1_color_list = user1.colors.all()
        user2_color_list = user2.colors.all()

        self.assertEqual(user_list.count(), 2)
        self.assertEqual(user1_color_list.count(), 1 + 1 + len(hex_color_list)) # ユーザーにはデフォルトで透明な色とデフォルトの色が追加される
        self.assertEqual(user2_color_list.count(), 1 + 1 + len(hex_color_list)) # ユーザーにはデフォルトで透明な色とデフォルトの色が追加される

        self.assertEqual(user_list[0].pk, user1.pk)
        self.assertEqual(user_list[1].pk, user2.pk)

    def test_one_user_have_two_colors_and_default_colors(self):
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        red = self.create_color(red='ff', green='00', blue='00')
        green = self.create_color(red='00', green='ff', blue='00')
        red.users.add(user)
        green.users.add(user)

        red_user_list = red.users.all()
        green_user_list = green.users.all()
        color_list = user.colors.all()

        self.assertEqual(red_user_list.count(), 1)
        self.assertEqual(green_user_list.count(), 1)
        self.assertEqual(color_list.count(), 2 + 1 + len(hex_color_list)) # ユーザーにはデフォルトで透明な色が追加される

        self.assertEqual(red_user_list[0].pk, user.pk)
        self.assertEqual(green_user_list[0].pk, user.pk)


class DiaryModelTests(TestCase):
    @classmethod
    def create_diary(cls, user, color, color_level, context):
        diary = Diary.objects.create(user=user, color=color, color_level=color_level, context=context)
        return diary

    def assertDiary(self, diary, user, color, color_level, created_at, updated_at, context):
        self.assertEqual(diary.user.pk, user.pk)
        self.assertEqual(diary.color.pk, color.pk)
        self.assertEqual(diary.color_level, color_level)
        self.assertTrue((diary.created_at - created_at) < datetime.timedelta(seconds=1))
        self.assertTrue((diary.updated_at - updated_at) < datetime.timedelta(seconds=1))
        self.assertEqual(diary.context, context)

    def test_create_diary(self):
        color = ColorModelTests.create_color('ff', '00', '00')
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        now = timezone.now()
        diary = self.create_diary(user=user, color=color, color_level=1, context=CONTEXT)

        get_diary = Diary.objects.get(pk=diary.pk, user=user) # いちいち保存したものを再び取ってきて、値を確認するのってテストになるのかな？わからないけどとりあえず書いてみよう。
        self.assertDiary(diary=get_diary, user=user, color=color, color_level=1, created_at=now, updated_at=now, context=CONTEXT)

    def test_on_delete_after_user_delete(self):
        color = ColorModelTests.create_color('ff', '00', '00')
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        diary = self.create_diary(user=user, color=color, color_level=1, context=CONTEXT)

        user.delete()

        with self.assertRaises(Diary.DoesNotExist):
            get_diary = Diary.objects.get(pk=diary.pk, user=user)

    def test_on_delete_after_color_delete(self):
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        color = ColorModelTests.create_color(red='ff', green='00', blue='00')
        diary = self.create_diary(user=user, color=color, color_level=1, context=CONTEXT)

        color.delete()

        get_diary = Diary.objects.get(pk=diary.pk, user=user)
        transparent = HexColor('ff', 'ff', 'ff', 0.0)
        self.assertEqual(get_diary.color.hex_color, transparent)

    def test_auto_now_add_and_auto_now_when_update(self):
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        color = ColorModelTests.create_color(red='ff', green='00', blue='00')
        then = timezone.now()
        diary = self.create_diary(user=user, color=color, color_level=1, context='')

        time.sleep(3)
        now = timezone.now()
        diary.context = CONTEXT
        diary.save()

        get_diary = Diary.objects.get(pk=diary.pk, user=user)
        self.assertDiary(diary=get_diary, user=user, color=color, color_level=1, created_at=then, updated_at=now, context=CONTEXT)

    def test_blank_context(self):
        user = UserModelTests.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        color = ColorModelTests.create_color(red='ff', green='00', blue='00')
        now = timezone.now()
        diary = self.create_diary(user=user, color=color, color_level=1, context='')
        get_diary = Diary.objects.get(pk=diary.pk, user=user)
        self.assertDiary(diary=get_diary, user=user, color=color, color_level=1, created_at=now, updated_at=now, context='')


