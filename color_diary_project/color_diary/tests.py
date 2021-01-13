from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from django.http.request import QueryDict

from .models import User
from .admin import UserCreationForm, UserChangeForm

EXAMPLE_EMAIL = 'example1@gmail.com'
EXAMPLE_EMAIL2 = 'example2@gmail.com'
PASSWORD1 = 'password1'
PASSWORD2 = 'password2'


class UserModelTests(TestCase):
    def create_user(self, email, password):
        user = User.objects.create_user(email=email, password=password)
        return user

    def create_superuser(self, email, password):
        user = User.objects.create_super_user(email=email, password=password)
        return user

    def test_email_expected(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        self.assertEqual(user.email, EXAMPLE_EMAIL)

    def test_password_expected(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        self.assertTrue(user.check_password(PASSWORD1))

    def test_is_not_staff_with_user(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        self.assertFalse(user.is_staff)

    def test_is_staff_with_superuser(self):
        superuser = self.create_superuser(EXAMPLE_EMAIL, PASSWORD1)
        self.assertTrue(superuser.is_staff)

    def test_is_active_with_user(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        self.assertTrue(user.is_active)

    def test_value_error_when_email_is_empty(self):
        with self.assertRaises(ValueError):
            user = self.create_user(email='', password=PASSWORD1)

    def test_str_of_user(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        user_string = str(user)
        self.assertEqual(user_string, EXAMPLE_EMAIL)

    def test_filter_by_right_email(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        user_queryset = get_user_model().objects.filter(email=EXAMPLE_EMAIL)
        self.assertQuerysetEqual(user_queryset, [f'<User: {EXAMPLE_EMAIL}>'])

    def test_filter_by_wrong_email(self):
        user = self.create_user(EXAMPLE_EMAIL, PASSWORD1)
        user_queryset = get_user_model().objects.filter(email=EXAMPLE_EMAIL2)
        self.assertQuerysetEqual(user_queryset, [])


class UserCreationFormTests(TestCase):
    def create_cleaned_user_creation_form(self, password1, password2, email):
        post = QueryDict(f'password1={password1}&password2={password2}&email={email}')
        form = UserCreationForm(post)
        form.is_valid()
        return form

    def test_clean_password2_with_unmatched_passwords(self):
        form = self.create_cleaned_user_creation_form(password1=PASSWORD1, password2=PASSWORD2, email=EXAMPLE_EMAIL)
        self.assertDictEqual(form.errors, {'password2': ["Passwords don't match."]})

    def test_clean_password2_with_matched_passwords(self):
        form = self.create_cleaned_user_creation_form(password1=PASSWORD1, password2=PASSWORD1, email=EXAMPLE_EMAIL)
        self.assertEqual(form.cleaned_data.get('password2'), PASSWORD1)

    def test_saved_password_matches_to_password(self):
        self.create_cleaned_user_creation_form(password1=PASSWORD1, password2=PASSWORD1, email=EXAMPLE_EMAIL).save()
        user = authenticate(email=EXAMPLE_EMAIL, password=PASSWORD1)
        self.assertEqual(user.email, EXAMPLE_EMAIL)
        self.assertTrue(user.check_password(PASSWORD1))


class UserChangeFormTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(email=EXAMPLE_EMAIL, password=PASSWORD1)

    def change_user_with_user_change_form(self, email=EXAMPLE_EMAIL, password=PASSWORD1, is_active=True, is_staff=False) -> User:
        user = get_user_model().objects.get(email=EXAMPLE_EMAIL)
        query_string = f'password={password}&email={email}&is_active={is_active}&is_staff={is_staff}'
        post = QueryDict(query_string)
        form = UserChangeForm(post, instance=user)
        form.full_clean()
        if form.is_valid():
            form.save()

        return user

    def test_password_as_the_first_after_change(self):
        user = self.change_user_with_user_change_form(password=PASSWORD2)
        self.assertTrue(user.check_password(PASSWORD1))

    def test_email_after_change(self):
        user = self.change_user_with_user_change_form(email=EXAMPLE_EMAIL2)
        self.assertEqual(user.email, EXAMPLE_EMAIL2)

    def test_is_active_after_change(self):
        user = self.change_user_with_user_change_form(is_active=False)
        self.assertFalse(user.is_active)

    def test_is_staff_after_change(self):
        user = self.change_user_with_user_change_form(is_staff=True)
        self.assertTrue(user.is_staff)