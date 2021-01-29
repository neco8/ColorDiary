from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME, authenticate

from .models import Diary, Color
from .fields import parse_hex_color
from .constant import *
from ..utils import get_hashids
from ..forms import DEFAULT_COLOR_LEVEL


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
        self.assertContains(response, 'invalid login.')
        self.assertContains(response, EXAMPLE_EMAIL)
        self.assertIsNone(response.request.get('password'))
        self.assertIsNotNone(response.context['error_message'])

    def test_redirect_when_login_succeeded(self):
        response = self.client.post(reverse('color_diary:login'), data={
            'email': EXAMPLE_EMAIL,
            'password': PASSWORD1,
        })
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_redirect_to_choose_color_view_after_logging_in(self):
        self.client.logout()
        hash_id = get_hashids().encode(self.diary.pk)
        redirect_url = reverse("color_diary:choose-color", kwargs={"diary_hash_id": hash_id})
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={redirect_url}'
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
        self.assertRedirects(response, reverse('color_diary:welcome'))


class RegisterViewTests(TestCase):
    def test_right_redirect_after_succeeding_register(self):
        response = self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD1,
        })
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_empty_form_with_get_request(self):
        response = self.client.get(reverse('color_diary:register'))
        form = response.context['form']
        self.assertIsNotNone(form.fields['email'])
        self.assertIsNotNone(form.fields['password1'])
        self.assertIsNotNone(form.fields['password2'])
        self.assertFalse(form.is_bound)

    def test_save_with_valid_data(self):
        response = self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD1,
        })
        user = authenticate(response.request, email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.assertIsNotNone(user)

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

    def test_login_after_succeeding_register(self):
        response = self.client.post(reverse('color_diary:register'), data={
            'email': EXAMPLE_EMAIL,
            'password1': PASSWORD1,
            'password2': PASSWORD1,
        })
        user = authenticate(response.request, email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.assertEqual(self.client.session.get('_auth_user_id'), str(user.pk))

class ChooseColorViewTests(TestCase):
    # todo: 色選択画面からは色一覧画面には行かせない。色追加だけできるようにする
    # todo: デフォルトカラーが選択できなかった。要修正
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

    def test_choose_color_view_with_not_login_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(0)
        choose_color_url = reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(choose_color_url)
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={choose_color_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_choose_color_get_when_creating_diary(self):
        hash_id = get_hashids().encode(0)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertContains(response, DEFAULT_COLOR_LEVEL)
        self.assertContains(response, '#FFFFFF')

    def test_choose_color_post_when_creating_diary(self):
        hash_id = get_hashids().encode(0)
        response = self.client.post(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}), {
            'color': self.red.pk,
            'color_level': 5,
        })
        self.assertEqual(response.client.session['color_id'], self.red.pk)
        self.assertEqual(response.client.session['color_level'], '5')
        self.assertRedirects(response, reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}))

    def test_choose_color_get_when_editing_diary(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertContains(response, self.diary.color_level)
        self.assertContains(response, self.diary.color.hex_color)

    def test_choose_color_post_when_editing_diary(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.post(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}), {
            'color': self.green.pk,
            'color_level': 4,
        })
        self.assertEqual(response.client.session['color_id'], self.green.pk)
        self.assertEqual(response.client.session['color_level'], '4')
        self.assertRedirects(response, reverse('color_diary:edit-diary', kwargs={'diary_hash_id': hash_id}))

    def test_invalid_hashid(self):
        with self.assertRaisesMessage(ValueError, expected_message='invalid diary hash id.'):
            self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': 'something389725hogehoge'}))

    def test_invalid_id(self):
        hash_id = get_hashids().encode(2111549857857)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_diary_id_of_other_user(self):
        hash_id = get_hashids().encode(self.diary_user2.pk)
        response = self.client.get(reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:diary-index'))



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

    def test_delete_diary_view_with_not_login_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(self.diary.pk)
        delete_diary_url = reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(delete_diary_url)
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={delete_diary_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_redirect_to_diary_index_after_deleting(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_delete_only_my_diary(self):
        my_diary_pk = self.diary.pk
        hash_id = get_hashids().encode(my_diary_pk)
        self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        with self.assertRaises(Diary.DoesNotExist):
            my_diary = Diary.objects.get(id=my_diary_pk, user=self.user)

    def test_cannot_delete_diary_of_other_user_and_redirect_to_diary_index(self):
        hash_id = get_hashids().encode(self.diary_of_user2.pk)
        response = self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_cannot_delete_diary_which_does_not_exist_and_redirect_to_diary_index(self):
        hash_id = get_hashids().encode(15875091750987325)
        response = self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:diary-index'))

    def test_contains_delete_string(self):
        hash_id = get_hashids().encode(self.diary.pk)
        response = self.client.get(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': hash_id}))
        self.assertContains(response, '完全に削除しますか？')

    def test_unable_to_encode_invalid_diary_hash_id(self):
        with self.assertRaisesMessage(ValueError, expected_message='invalid diary hash id.'):
            self.client.post(reverse('color_diary:delete-diary', kwargs={'diary_hash_id': 'somethingOFhoGeHOGe'}))


class DeleteColorViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.user_color = Color.objects.create(hex_color=parse_hex_color('ff0000'))
        self.user_color.users.add(self.user)
        
        self.user2 = get_user_model().objects.create_user(email=EXAMPLE_EMAIL2, password=PASSWORD2)
        self.user2_color = Color.objects.create(hex_color=parse_hex_color('00ff00'))
        self.user2_color.users.add(self.user2)
        
        self.client.login(email=EXAMPLE_EMAIL, password=PASSWORD1)
        
    def test_delete_color_view_with_not_login_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(self.user_color.pk)
        delete_color_url = reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id})
        response_before_login = self.client.get(delete_color_url)
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={delete_color_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_redirect_to_color_index_after_deleting(self):
        hash_id = get_hashids().encode(self.user_color.pk)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:color-index'))

    def test_can_delete_my_color_relationship_and_color_object_still_exist(self):
        hash_id = get_hashids().encode(self.user_color.pk)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertEqual(Color.objects.filter(id=self.user_color.pk).count(), 1)
        self.assertEqual(self.user.colors.filter(id=self.user_color.pk).count(), 0)

    def test_cannot_delete_color_of_other_user_and_redirect_to_color_index(self):
        hash_id = get_hashids().encode(self.user2_color.pk)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:color-index'))
        self.assertEqual(self.user2.colors.filter(id=self.user2_color.pk).count(), 1)

    def test_cannot_delete_color_which_does_not_exist_and_redirect_to_color_index(self):
        hash_id = get_hashids().encode(195701735187)
        response = self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': hash_id}))
        self.assertRedirects(response, reverse('color_diary:color-index'))

    def test_unable_to_encode_invalid_color_hash_id(self):
        with self.assertRaisesMessage(ValueError, expected_message='invalid color hash id.'):
            self.client.post(reverse('color_diary:delete-color', kwargs={'color_hash_id': 'soMEthingOFHOgehoGEhoge'}))


class EditDiaryViewTests(TestCase):
# todo: データベースに変更があるものはリダイレクトされるか確認する
# todo: 自動保存されるかどうか。恐らくvue.jsの方で仕組みを作る事になる
# todo: 操作できるのは自分のユーザーだけ
#まず日記一覧画面がある
#そして色選択画面がある。編集か追加に限らない。
#色選択画面で色とレベルを送信したら、それをこのviewで受け取る
#色とレベルをinstanceの中に入れて、context空で表示する
#contextを編集して、送信ボタンを押せば日記を作成、保存する
#そしたら日記一覧画面に戻る
    def setUp(self) -> None:
        pass

    def test_choose_color_view_with_not_login_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(0)
        choose_color_url = reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(choose_color_url)
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={choose_color_url}'
        self.assertRedirects(response_before_login, login_url)
    def test_edit_diary_view_with_not_login_user(self):
        pass

    def test_create_diary(self):
        # しっかり色編集画面カラーピッカーが表示されるかどうか
        pass

    def test_edit_diary(self):
        # しっかり以前作った日記が表示されるかどうか
        pass


class EditColorViewTests(TestCase):
# todo: データベースに変更があるものはリダイレクトされるか確認する
# todo: 将来的にカラーピッカーを追加する
# todo: 操作できるのは自分のユーザーだけ
#まず色一覧画面が表示される
#色一覧画面のなかで追加ボタンがある
#追加ボタンもしくは色編集を押すとこの画面に行く
#instanceがあるならそれを持ってきてcolor_codeを入力する
#ないなら新規で作る。
    def setUp(self) -> None:
        pass

    def test_choose_color_view_with_not_login_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(0)
        choose_color_url = reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(choose_color_url)
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={choose_color_url}'
        self.assertRedirects(response_before_login, login_url)
    def test_edit_color_view_with_not_login_user(self):
        pass

    def test_create_color(self):
        # しっかり空日記、時間があっている日記が表示されるかどうか
        pass

    def test_edit_color(self):
        # しっかり以前作った日記が表示されるかどうか
        pass


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

    def test_diary_index_view_with_not_login_user(self):
        self.client.logout()
        choose_color_url = reverse('color_diary:diary-index')
        response_before_login = self.client.get(choose_color_url)
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={choose_color_url}'
        self.assertRedirects(response_before_login, login_url)

    def test_two_diaries(self):
        response = self.client.get(reverse('color_diary:diary-index'))
        self.assertQuerysetEqual(response.context['diary_list'], [f'<Diary: Diary object ({self.new_diary.pk})>', f'<Diary: Diary object ({self.old_diary.pk})>'])
        # order created_at

    def test_older_one_update(self):
        response = self.client.get(reverse('color_diary:diary-index'))
        self.old_diary.context = 'this is an updated old diary.'
        self.assertQuerysetEqual(response.context['diary_list'], [f'<Diary: Diary object ({self.new_diary.pk})>', f'<Diary: Diary object ({self.old_diary.pk})>'])


class ColorIndexViewTests(TestCase):
# todo: 操作できるのは自分のユーザーだけ
    def test_choose_color_view_with_not_login_user(self):
        self.client.logout()
        hash_id = get_hashids().encode(0)
        choose_color_url = reverse('color_diary:choose-color', kwargs={'diary_hash_id': hash_id})
        response_before_login = self.client.get(choose_color_url)
        login_url = f'/color-diary/login/?{REDIRECT_FIELD_NAME}={choose_color_url}'
        self.assertRedirects(response_before_login, login_url)


class WelcomeViewTests(TestCase):
    pass