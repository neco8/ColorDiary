from django.test import TestCase

from .models import User, UserManager


class UserModelTests(TestCase):
    def create_user(self, email, password):
        user = User.objects.create_user(email=email, password=password)
        return user

    def create_superuser(self, email, password):
        user = User.objects.create_super_user(email=email, password=password)
        return user

    def test_email_expected(self):
        user = self.create_user('a@b.c', 'test')
        self.assertEqual(user.email, 'a@b.c')

    def test_is_not_staff_with_user(self):
        user = self.create_user('a@b.c', 'test')
        self.assertFalse(user.is_staff)

    def test_is_active_with_user(self):
        user = self.create_user('a@b.c', 'test')
        self.assertTrue(user.is_active)

    def test_is_staff_with_superuser(self):
        superuser = self.create_superuser('a@b.c', 'test')
        self.assertTrue(superuser.is_staff)

    def test_value_error_when_email_is_empty(self):
        with self.assertRaises(ValueError):
            user = self.create_user(email='', password='test')

    def test_str_of_user(self):
        user = self.create_user('a@b.c', 'test')
        user_string = str(user)
        self.assertEqual(user_string, 'a@b.c')
