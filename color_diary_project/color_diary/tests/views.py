import re
import logging

from django.test import TestCase
from django.urls import reverse
from django.core.signing import dumps
from django.core import mail
from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME, authenticate
from django.utils import timezone

from .models import Diary, Color
from .fields import parse_hex_color
from .constant import *
from ..utils import get_hashids
from ..forms import DEFAULT_COLOR_LEVEL
from ..views import CREATE


logger = logging.getLogger(__name__)


class LoginViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.red = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.red.users.add(self.user)
        self.diary = Diary.objects.create(user=self.user, color=self.red, color_level=8, context=CONTEXT)

    def test_empty_form(self):
        response = self.client.get(reverse('color_diary:login'))
        self.assertContains(response, 'email')
        self.assertContains(response, 'password')

    def test_invalid_login_message_and_email(self):
        response = self.client.post(reverse('color_diary:login'), data={
            'email': EXAMPLE_EMAIL,
            'password': PASSWORD2
        })
        self.assertContains(response, 'Email or Password is invalid.')
        self.assertContains(response, EXAMPLE_EMAIL)
        self.assertIsNone(response.request.get('password'))

    def test_redirect_to_diary_index_view_when_login_succeeded(self):
        response = self.client.post(reverse('color_diary:login'), data={
            'email': EXAMPLE_EMAIL,
            'password': PASSWORD1,
        })
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_redirect_to_choose_color_view_after_logging_in_when_visited(self):
        self.client.logout()
        hash_id = get_hashids().encode(self.diary.pk)
        redirect_url = reverse("color_diary:choose-color", kwargs={"diary_hash_id": hash_id})
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={redirect_url}'
        response = self.client.post(login_url, data={
            'email': EXAMPLE_EMAIL,
            'password': PASSWORD1,
        })
        self.assertRedirects(response, redirect_url)


class LogoutViewTests(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)

    def test_logout_redirect_to_welcome(self):
        response = self.client.get(reverse('color_diary:logout'))
        self.assertEqual(len(self.client.session.keys()), 0)
        self.assertRedirects(response, reverse('color_diary:top'))


class RegisterViewTests(TestCase):
    def test_right_redirect_after_pre_register(self):
        response = self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD1,
        })
        self.assertRedirects(response, reverse('color_diary:register-done'))

    def test_get_request(self):
        response = self.client.get(reverse('color_diary:register'))
        form = response.context['form']
        self.assertIsNotNone(form.fields['email'])
        self.assertIsNotNone(form.fields['password1'])
        self.assertIsNotNone(form.fields['password2'])
        self.assertFalse(form.is_bound)

    def test_error_message_with_invalid_data(self):
        response = self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD2,
        })
        form = response.context['form']
        self.assertContains(response, "Passwords don&#x27;t match.")
        self.assertEqual(form.cleaned_data['email'], EXAMPLE_EMAIL)
        self.assertEqual(form.cleaned_data['password1'], PASSWORD1)
        self.assertIsNone(form.cleaned_data.get('password2', None))

    def test_email_after_pre_register(self):
        mail.outbox = []
        self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD1,
        })
        self.assertEqual(len(mail.outbox), 1)

    def test_save_user_after_succeeding_register(self):
        self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD1,
        })
        mail_message = mail.outbox[-1].body
        token = re.search(r'register/(.+?)/', mail_message).group(1)
        response = self.client.get(reverse('color_diary:register-complete', kwargs={'token': token}))

        user = authenticate(response.request, email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.assertIsNotNone(user)

    def test_login_after_succeeding_register(self):
        self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD1,
        })
        mail_message = mail.outbox[-1].body
        token = re.search(r'register/(.+?)/', mail_message).group(1)
        response = self.client.get(reverse('color_diary:register-complete', kwargs={'token': token}))

        user = authenticate(response.request, email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.assertEqual(self.client.session.get('_auth_user_id'), str(user.pk))

class ChooseColorViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.red = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.green = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.user.colors.add(self.red, self.green)
        self.diary = Diary.objects.create(user=self.user, color=self.red, color_level=8, context=CONTEXT)

        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        self.user2.colors.add(self.red)
        self.diary_user2 = Diary.objects.create(user=self.user2, color=self.red, color_level=1, context=CONTEXT)

        self.client.login(username=EXAMPLE_EMAIL, password=PASSWORD1)

    def test_choose_color_view_with_anonymous_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(0)
        choose_color_url = reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(choose_color_url)
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={choose_color_url}'
        self.assertRedirects(response_before_login, login_url)

    # 日記新規作成
    def test_choose_color_with_get_request_when_creating_diary(self):
        hash_id = get_hashids().encode(0)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertContains(response, DEFAULT_COLOR_LEVEL)
        self.assertContains(response, '#FFFFFF')

    def test_choose_color_session_with_post_request_when_creating_diary(self):
        hash_id = get_hashids().encode(0)
        response = self.client.post(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}), {
            'color': self.red.pk,
            'color_level': 5,
        })
        self.assertEqual(self.client.session['color_id'], self.red.pk)
        self.assertEqual(self.client.session['color_level'], 5)

    def test_redirect_to_edit_diary_when_creating_diary(self):
        hash_id = get_hashids().encode(0)
        response = self.client.post(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}), {
            'color': self.red.pk,
            'color_level': 5,
        })
        self.assertRedirects(response, reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}))

    # 日記編集
    def test_choose_color_with_get_request_when_editing_diary(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertContains(response, self.diary.color_level)
        self.assertContains(response, self.diary.color.hex_color)

    def test_choose_color_session_with_post_request_when_editing_diary(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.post(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}), {
            'color': self.green.pk,
            'color_level': 4,
        })
        self.assertEqual(self.client.session['color_id'], self.green.pk)
        self.assertEqual(self.client.session['color_level'], 4)

    def test_redirect_to_edit_diary_when_editing_diary(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.post(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}), {
            'color': self.green.pk,
            'color_level': 4,
        })
        self.assertRedirects(response, reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}))

    def test_get_request_404_with_invalid_hash_id(self):
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': 'something389725hogehoge'}))
        self.assertEqual(response.status_code, 404)

    def test_get_request_404_with_invalid_id(self):
        hash_id = get_hashids().encode(2111549857857)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)

    def test_get_request_404_with_diary_id_of_other_user(self):
        hash_id = get_hashids().encode(self.diary_user2.pk)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)


class DeleteDiaryViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.red = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.red.users.add(self.user)
        self.diary = Diary.objects.create(user=self.user, color=self.red, color_level=6, context=CONTEXT)

        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        self.green = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.green.users.add(self.user2)
        self.diary_of_user2 = Diary.objects.create(user=self.user2, color=self.green, color_level=6, context=CONTEXT)

        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)

    def test_delete_diary_view_with_anonymous_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(self.diary.pk)
        delete_diary_url = reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(delete_diary_url)
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={delete_diary_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_redirect_to_diary_index_view_after_deleting(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_delete_my_diary(self):
        my_diary_pk = self.diary.pk
        hash_id = get_hashids().encode(my_diary_pk)
        self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        with self.assertRaises(Diary.DoesNotExist):
            my_diary = Diary.objects.get(id=my_diary_pk, user=self.user)

    def test_cannot_delete_other_user_s_diary_and_return_404(self):
        hash_id = get_hashids().encode(self.diary_of_user2.pk)
        response = self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_diary_which_does_not_exist_and_return_404(self):
        hash_id = get_hashids().encode(15875091750987325)
        response = self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)

    def test_contains_delete_string(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.get(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertContains(response, '完全に削除しますか？')

    def test_unable_to_encode_invalid_diary_hash_id_and_return_404(self):
        response = self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': 'somethingOFhoGeHOGe'}))
        self.assertEqual(response.status_code, 404)


class DeleteColorViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.user_color = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.user_color2 = Color.objects.create(hex_color=parse_hex_color('0000ff'))
        self.user.colors.add(self.user_color, self.user_color2)

        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        self.user2_color = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.user2_color.users.add(self.user2)
        self.user_color.users.add(self.user2)

        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)

    def test_delete_color_view_with_anonymous_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(self.user_color.pk)
        delete_color_url = reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id})
        response_before_login = self.client.get(delete_color_url)
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={delete_color_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_redirect_to_color_index_view_after_deleting(self):
        hash_id = get_hashids().encode(self.user_color.pk)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:color-index'))

    def test_delete_only_color_relationship_and_color_object_still_exist(self):
        hash_id = get_hashids().encode(self.user_color.pk)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertEqual(Color.objects.filter(id=self.user_color.pk).count(), 1)
        self.assertEqual(self.user.colors.filter(id=self.user_color.pk).count(), 0)

    def test_cannot_delete_other_user_s_color_and_return_404(self):
        hash_id = get_hashids().encode(self.user2_color.pk)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user2.colors.filter(id=self.user2_color.pk).count(), 1)

    def test_cannot_delete_color_which_does_not_exist_and_return_404(self):
        hash_id = get_hashids().encode(195701735187)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)

    def test_unable_to_encode_invalid_color_hash_id_and_return_404(self):
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': 'soMEthingOFHOgehoGEhoge'}))
        self.assertEqual(response.status_code, 404)

    def test_delete_color_that_belongs_to_one_user_and_then_object_deleted(self):
        hash_id = get_hashids().encode(self.user_color2.pk)
        self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertEqual(Color.objects.filter(hex_color=parse_hex_color('0000ff')).count(), 0)


class EditDiaryViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.user_color1 = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.user.colors.add(self.user_color1)

        self.diary_user1 = Diary.objects.create(user=self.user, color=self.user_color1, color_level=6, context=CONTEXT)

        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)

    def test_edit_diary_view_with_anonymous_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(CREATE)
        edit_diary_url = reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(edit_diary_url)
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={edit_diary_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_get_request_when_creating_diary(self):
        hash_id = get_hashids().encode(CREATE)

        session = self.client.session
        session['color_id'] = self.user_color1.pk
        session['color_level'] = 3
        session.save()

        response = self.client.get(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}))
        form = response.context['form']
        self.assertFalse(form.is_bound)

    def test_get_request_when_editing_diary(self):
        hash_id = get_hashids().encode(self.diary_user1.pk)

        session = self.client.session
        session['color_id'] = self.user_color1.pk
        session['color_level'] = 3
        session.save()

        response = self.client.get(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}))
        form = response.context['form']
        self.assertFalse(form.is_bound)
        self.assertContains(response, self.diary_user1.context)

    def test_save(self):
        hash_id = get_hashids().encode(CREATE)
        now = timezone.now()

        self.client.post(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}), data={
            'context': CONTEXT,
            'color': self.user_color1.pk,
            'color_level': 3,
        })
        diary = Diary.objects.all(user=self.user).order_by('-created_at')[0]
        self.assertEqual(diary.user, self.user)
        self.assertEqual(diary.color, self.user_color1)
        self.assertEqual(diary.color_level, 3)
        self.assertTrue(now - diary.created_at < timezone.timedelta(seconds=1))
        self.assertTrue(now - diary.updated_at < timezone.timedelta(seconds=1))
        self.assertEqual(diary.context, CONTEXT)

    def test_redirect_to_diary_index_view_after_saving_object(self):
        hash_id = get_hashids().encode(self.diary_user1.pk)

        response = self.client.post(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}), data={
            'context': CONTEXT,
            'color': self.user_color1.pk,
            'color_level': 3,
        })
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_get_return_http_404_with_invalid_hash_id(self):
        session = self.client.session
        session['color_id'] = self.user_color1.pk
        session['color_level'] = 3
        session.save()

        response = self.client.get(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': 'tekitounaMOJIretsu'}))
        self.assertEqual(response.status_code, 404)

    def test_post_return_404_with_invalid_hash_id(self):
        response = self.client.post(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': 'tekitounaMOJIretsu'}), data={
            'color': self.user_color1.pk,
            'color_level': 3
        })
        self.assertEqual(response.status_code, 404)

    def test_get_return_404_with_invalid_diary_id(self):
        hash_id = get_hashids().encode(987315937)

        session = self.client.session
        session['color_id'] = self.user_color1.pk
        session['color_level'] = 3
        session.save()

        response = self.client.get(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)

    def test_post_return_404_with_invalid_diary_id(self):
        hash_id = get_hashids().encode(987315937)

        response = self.client.post(reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}), data={
            'color': self.user_color1.pk,
            'color_level': 3
        })
        self.assertEqual(response.status_code, 404)


class EditColorViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.default_color = Color.get_default_color()
        self.user_color1 = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.user_color1.users.add(self.user)

        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        self.user2_color1 = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.user2_color1.users.add(self.user2)

        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)

    def test_edit_color_view_with_anonymous_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(CREATE)
        edit_color_url = reverse('color_diary:edit-color', kwargs={'color_hash_id': hash_id})
        response_before_login = self.client.get(edit_color_url)
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={edit_color_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_get_request_404_when_editing_default_color(self):
        hash_id = get_hashids().encode(self.default_color.pk)
        response = self.client.get(reverse('color_diary:edit-color', kwargs={'color_hash_id': hash_id}))
        self.assertEqual(response.status_code, 404)

    def test_post_request_404_when_editing_default_color(self):
        hash_id = get_hashids().encode(self.default_color.pk)
        response = self.client.post(reverse('color_diary:edit-color', kwargs={'color_hash_id': hash_id}), data={'hex_color': 'f8f8f8'})
        self.assertEqual(response.status_code, 404)

    def test_initial_hex_color_with_get_request_when_creating_color(self):
        hash_id = get_hashids().encode(CREATE)
        response = self.client.get(reverse('color_diary:edit-color', kwargs={'color_hash_id': hash_id}))
        self.assertContains(response, '000000')

    def test_initial_hex_color_with_get_request_when_editing_color(self):
        hash_id = get_hashids().encode(self.user_color1.pk)
        response = self.client.get(reverse('color_diary:edit-color', kwargs={'color_hash_id': hash_id}))
        self.assertContains(response, 'FF0000')

    def test_post_request_with_valid_hex_color(self):
        hash_id = get_hashids().encode(self.user_color1.pk)

        session = self.client.session
        session['previous_url'] = reverse('color_diary:diary-index')
        session.save()

        self.client.post(reverse('color_diary:edit-color', kwargs={'color_hash_id': hash_id}), data={
            'hex_color': '00ff00'
        })
        self.assertEqual(self.user2_color1.users.all().count(), 2)
        self.assertEqual(self.user_color1.users.all().count(), 0)

    def test_post_request_with_invalid_hex_color(self):
        hash_id = get_hashids().encode(self.user_color1.pk)
        response = self.client.post(reverse('color_diary:edit-color', kwargs={'color_hash_id': hash_id}), data={
            'hex_color': 'zzzzzzzz'
        })
        self.assertContains(response, 'error')


class DiaryIndexViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.color = Color.objects.create(hex_color=parse_hex_color('ff0000'))

        self.old_diary = Diary.objects.create(user=self.user, color=self.color, color_level=8, context='this is an old diary.')
        self.new_diary = Diary.objects.create(user=self.user, color=self.color, color_level=8, context='this is a new diary.')

        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        self.color_user2 = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.color_user2.users.add(self.user2)

        self.diary_of_other_user = Diary.objects.create(user=self.user2, color=self.color_user2, color_level=8, context="this is other user's diary.")

    def test_diary_index_view_with_anonymous_user(self):
        self.client.logout()
        diary_index_url = reverse('color_diary:diary-index')
        response_before_login = self.client.get(diary_index_url)
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={diary_index_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_diary_index_with_two_diaries(self):
        response = self.client.get(reverse('color_diary:diary-index'))
        self.assertQuerysetEqual(response.context['diary_list'], [f'<Diary: Diary object ({self.new_diary.pk})>', f'<Diary: Diary object ({self.old_diary.pk})>'])

    def test_diary_index_when_older_one_updates(self):
        response = self.client.get(reverse('color_diary:diary-index'))
        self.old_diary.context = 'this is an updated old diary.'
        self.assertQuerysetEqual(response.context['diary_list'], [f'<Diary: Diary object ({self.new_diary.pk})>', f'<Diary: Diary object ({self.old_diary.pk})>'])


class ColorIndexViewTests(TestCase):
    def setUp(self) -> None:
        # 赤から緑から青
        # 彩度高い方が大きい
        # 黒の方が大きい
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        # #FFFFFF-0.0
        self.user_color1 = Color.objects.create(hex_color=parse_hex_color('000000')) # 無彩色は一番最初に来る
        self.user_color2 = Color.objects.create(hex_color=parse_hex_color('ff1919')) # 彩度が低い
        self.user_color3 = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.user_color4 = Color.objects.create(hex_color=parse_hex_color('e60000')) # より黒い
        self.user_color5 = Color.objects.create(hex_color=parse_hex_color('ff2a00')) # 色相が高い
        # #F7774D-1.0
        self.user_color6 = Color.objects.create(hex_color=parse_hex_color('ff5400')) # さらに色相が高い
        # #F9BB2B-1.0, #B7BF19-1.0, #00A583-1.0, #008FB3-1.0, #4D73BB-1.0, #9C5DA0-1.0, #D75674-1.0
        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        self.user2_color1 = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.user2_color2 = Color.objects.create(hex_color=parse_hex_color('00ff11'))

        self.user.colors.add(self.user_color1, self.user_color2, self.user_color3, self.user_color4, self.user_color5, self.user_color6)
        self.user2.colors.add(self.user2_color1, self.user2_color2)

        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)

    def test_color_index_view_with_anonymous_user(self):
        self.client.logout()
        color_index_url = reverse('color_diary:color-index')
        response_before_login = self.client.get(color_index_url)
        login_url = f'/login/?{REDIRECT_FIELD_NAME}={color_index_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_order_of_color(self):
        response = self.client.get(reverse('color_diary:color-index'))
        l = response.context['color_list']
        self.assertEqual([str(color) for color in response.context['color_list']], [
            f'{Color.get_default_color()}',
            f'{self.user_color1}',
            f'{self.user_color2}',
            f'{self.user_color3}',
            f'{self.user_color4}',
            f'{self.user_color5}',
            '#F7774D-1.0',
            f'{self.user_color6}',
            '#F9BB2B-1.0', '#B7BF19-1.0', '#00A583-1.0', '#008FB3-1.0', '#4D73BB-1.0', '#9C5DA0-1.0', '#D75674-1.0'
        ])

    def test_disabled_link_of_default_color(self):
        response = self.client.get(reverse('color_diary:color-index'))
        self.assertContains(response, 'FFFFFF')


class WelcomeViewTests(TestCase):
    pass