from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Profile
from ..views import ProfileTopListView


class ProfileTopListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(20):
            get_user_model().objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password=f'user{i}pass')
        cls.profiles = Profile.objects.order_by('pk').all()
        cls.PROFILE_LIST_URL = reverse('accounts:profile_list')

    def test_unlogged_in_user_gets_redirected(self):
        response = self.client.get('/account/profiles')
        expected_url = f'{reverse(settings.LOGIN_URL)}'
        expected_url += f'?next={ProfileTopListViewTest.PROFILE_LIST_URL}'
        self.assertRedirects(response, expected_url=expected_url)

    def test_view_exists_at_desired_location(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get('/account/profiles')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         ProfileTopListView.as_view().__name__)

    def test_view_url_is_accessible_by_name(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(ProfileTopListViewTest.PROFILE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         ProfileTopListView.as_view().__name__)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(ProfileTopListViewTest.PROFILE_LIST_URL)
        self.assertTemplateUsed(response, 'accounts/profile_list.html')

    def test_profiles_are_paginated(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(ProfileTopListViewTest.PROFILE_LIST_URL)
        self.assertIn('is_paginated', response.context)
        self.assertIn('page_obj', response.context)

    def test_each_page_contains_correct_number_of_profiles(self):
        self.client.login(username='user1', password='user1pass')

        url = f'{ProfileTopListViewTest.PROFILE_LIST_URL}'  # page 1
        response = self.client.get(ProfileTopListViewTest.PROFILE_LIST_URL)
        self.assertEqual(len(response.context['profiles']), 12)

        url = f'{ProfileTopListViewTest.PROFILE_LIST_URL}?page=1'
        response = self.client.get(url)
        self.assertEqual(len(response.context['profiles']), 12)

        url = f'{ProfileTopListViewTest.PROFILE_LIST_URL}?page=2'
        response = self.client.get(url)
        self.assertEqual(len(response.context['profiles']), 8)

    def test_each_rendered_page_contains_pagination_links(self):
        self.client.login(username='user1', password='user1pass')
        for i in range(1, 3):
            response = self.client.get(
                ProfileTopListViewTest.PROFILE_LIST_URL + f'?page={i}')
            for j in range(1, 3):
                self.assertContains(response, f'href="?page={j}"')

    def test_user_sees_all_profiles(self):
        self.client.login(username='user1', password='user1pass')

        url = f'{ProfileTopListViewTest.PROFILE_LIST_URL}?page=1'
        response = self.client.get(url)

        for profile in ProfileTopListViewTest.profiles[:12]:
            self.assertContains(response, profile.name)

        url = f'{ProfileTopListViewTest.PROFILE_LIST_URL}?page=2'
        response = self.client.get(url)

        for profile in ProfileTopListViewTest.profiles[12:]:
            self.assertContains(response, profile.name)
