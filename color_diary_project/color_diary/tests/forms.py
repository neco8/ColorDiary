import re

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Color, Diary
from ..forms import ChooseColorForm, ColorModelForm, DiaryModelForm
from ..fields import parse_hex_color
from .constant import *



class ChooseColorFormTests(TestCase):
    def setUp(self) -> None:
        self.red = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.green = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.black = Color.objects.create(hex_color=parse_hex_color('000000'))
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)

        self.user.colors.add(self.red, self.green)

    def test_is_valid(self):
        form = ChooseColorForm(login_user=self.user, data={
            'color': self.red,
            'color_level': 10,
        })
        is_valid = form.is_valid()
        self.assertQuerysetEqual(form.fields['color'].queryset, ['<Color: #FFFFFF-0.0>', '<Color: #FF0000-1.0>', '<Color: #00FF00-1.0>'])
        self.assertTrue(is_valid)

    def test_is_not_valid_with_wrong_color(self):
        form = ChooseColorForm(login_user=self.user, data={
            'color': self.black,
            'color_level': 10
        })
        is_valid = form.is_valid()
        self.assertQuerysetEqual(form.fields['color'].queryset, ['<Color: #FFFFFF-0.0>', '<Color: #FF0000-1.0>', '<Color: #00FF00-1.0>'])
        self.assertFalse(is_valid)
        self.assertEqual(form.errors['color'], ['Select a valid choice. That choice is not one of the available choices.'])

    def test_is_not_valid_with_wrong_color_level(self):
        form = ChooseColorForm(login_user=self.user, data={
            'color': self.red,
            'color_level': 100,
        })
        is_valid = form.is_valid()
        self.assertQuerysetEqual(form.fields['color'].queryset, ['<Color: #FFFFFF-0.0>', '<Color: #FF0000-1.0>', '<Color: #00FF00-1.0>'])
        self.assertFalse(is_valid)
        self.assertEqual(form.errors['color_level'], ['Select a valid choice. 100 is not one of the available choices.'])

    def test_do_not_give_user_argument(self):
        with self.assertRaisesMessage(ValueError, expected_message='the user argument is not given.'):
            form = ChooseColorForm(data={
                'color': self.red,
                'color_level': 10,
            })



class ColorModelFormTests(TestCase):
    def setUp(self) -> None:
        self.red = Color.objects.create(parse_hex_color('ff0000'))
        self.user1 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.red.users.add(self.user1)

        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)


    def test_is_valid(self):
        form = ColorModelForm(user=self.user1, data={
            'hex_color': 'ffffff',
        })
        is_valid = form.is_valid()
        self.assertTrue(is_valid)

    def test_create_color_that_is_already_created(self):
        form = ColorModelForm(user=self.user2, data={
            'hex_color': 'ff0000',
        })
        if form.is_valid():
            form.save()

        self.assertEqual(self.user2.colors.get(hex_color=parse_hex_color('ff0000')).pk, self.red.pk)

    def test_delete_color_when_previous_color_does_not_have_users_after_editing_color(self):
        form = ColorModelForm(user=self.user1, instance=self.red, data={
            'hex_color': '00ff00',
        })
        if form.is_valid():
            form.save()

        self.assertEqual(Color.objects.filter(hex_color=parse_hex_color('ff0000')).count(), 0)

    def test_editing_color_does_not_affect_when_color_belongs_to_some_users(self):
        self.red.users.add(self.user2)
        form = ColorModelForm(user=self.user1, instance=self.red, data={
            'hex_color': '0f0f0f',
        })
        if form.is_valid():
            form.save()
        self.assertEqual(self.user2.colors.filter(hex_color=parse_hex_color('ff0000')).count(), 1)

    def test_is_not_valid_with_not_hex_color_code(self):
        with self.assertRaisesMessage(ValueError, expected_message='RGB must be hex.'):
            form = ColorModelForm(user=self.user1, data={
                'hex_color': 'zzzzzz',
            })
            form.is_valid()

    def test_is_not_valid_with_wrong_hex_color(self):
        form = ColorModelForm(user=self.user1, data={
            'hex_color': 'ffffffffffffffffffffffff',
        })
        is_valid = form.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(form.errors['hex_color'], ['hex color code is too long.'])

    def test_is_not_valid_with_alpha_hex_color(self):
        form = ColorModelForm(user=self.user1, data={
            'hex_color': 'ffffff0.5',
        })
        is_valid = form.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(form.errors['hex_color'], ['hex color code is too long.'])

    def test_save(self):
        form = ColorModelForm(user=self.user1, data={
            'hex_color': 'f0f0f0',
        })
        if form.is_valid():
            form.save()
        color = Color.objects.get(hex_color=parse_hex_color('f0f0f0'))
        self.assertEqual(color.users.all().count(), 1)
        self.assertEqual(color.hex_color, parse_hex_color('f0f0f0'))

    def test_do_not_show_alpha(self):
        form = ColorModelForm(user=self.user1, instance=self.red)
        form_string = str(form)
        search_result = re.search(r'"FF0000"', form_string)
        self.assertIsNotNone(search_result)

    def test_do_not_give_user_argument(self):
        form = ColorModelForm(data={'hex_color': '888888'})
        form.is_valid()
        self.assertEqual(form.errors['__all__'], ['the user argument is required.'])

    def test_can_not_edit_default_color(self):
        form = ColorModelForm(
            user=self.user1,
            instance=Color.get_default_color(),
        )
        search_result = re.search(r'disabled', str(form))
        self.assertIsNotNone(search_result)


    def test_can_not_save_and_change_default_color(self):
        form = ColorModelForm(
            user=self.user1,
            instance=Color.get_default_color(),
            data={'hex_color': '888888'}
        )
        if form.is_valid():
            form.save()
        self.assertEqual(Color.objects.filter(hex_color=parse_hex_color('888888')).count(), 0)


class DiaryModelFormTests(TestCase):
    def setUp(self) -> None:
        self.red = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.user.colors.add(self.red)

        self.black = Color.objects.create(hex_color=parse_hex_color('000000'))

    def test_is_valid_true_with_valid_value(self):
        form = DiaryModelForm(
            user=self.user,
            color=self.red,
            data={
                'color': self.red.id,
                'color_level': 10,
                'created_at': '',
                'context': CONTEXT
            })
        form.is_valid()
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_is_valid_false_without_user(self):
        with self.assertRaises(Diary.user.RelatedObjectDoesNotExist):
            form = DiaryModelForm(
                color=self.red,
                color_level=10,
                data={
                    'color': self.red.id,
                    'color_level': 10,
                    'created_at': '',
                    'context': CONTEXT
                })
            form.is_valid()
            self.assertTrue(['the user argument is required.'] in form.errors.values())

    def test_is_valid_false_without_color(self):
        with self.assertRaises(Diary.color.RelatedObjectDoesNotExist):
            form = DiaryModelForm(
                user=self.user,
                color_level=10,
                data={
                    'color_level': 10,
                    'created_at': '',
                    'context': CONTEXT
                })
            form.is_valid()

    def test_is_valid_false_without_color_level(self):
        form = DiaryModelForm(
            user=self.user,
            color=self.red,
            data={
                'color': self.red.id,
                'created_at': '',
                'context': CONTEXT
            })
        form.is_valid()
        self.assertEqual(form.errors['color_level'], ['This field is required.'])

    def test_is_valid_false_with_wrong_color(self):
        form = DiaryModelForm(
            user=self.user,
            color=self.black,
            data={
                'color': self.black.id,
                'color_level': 10,
                'created_at': '',
                'context': CONTEXT
            }
        )
        form.is_valid()
        self.assertTrue(["this is invalid color. you don't have this color."] in form.errors.values())

    def test_save(self):
        form = DiaryModelForm(
            user=self.user,
            color=self.red,
            color_level=10,
            data={
                'color': self.red.id,
                'color_level': 10,
                'created_at': '',
                'context': CONTEXT
            }
        )
        if form.is_valid():
            saved_diary = form.save()
        diary = Diary.objects.get(user=self.user, id=saved_diary.id)
        
        self.assertEqual(diary.color, self.red)
        self.assertEqual(diary.color_level, 10)