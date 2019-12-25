from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Profile


class profileModelTest(TestCase):
    def test_profile_is_created_when_user_is_created(self):
        user = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        self.assertEqual(Profile.objects.count(), 1)

        profile = Profile.objects.first()

        self.assertEqual(profile.user, user)

    def test_profile_is_assigned_name_on_creation(self):
        user = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        profile = Profile.objects.first()

        self.assertEqual(profile.name, user.username)

    def test_profile_str_returns_profile_name(self):
        get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        profile = Profile.objects.first()

        self.assertEqual(str(profile), profile.name)

    def test_profile_get_absolute_url_returns_correct_url(self):
        get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        profile = Profile.objects.first()

        expected_url = '/account/user1/'
        self.assertEqual(profile.get_absolute_url(), expected_url)
