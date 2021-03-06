from itertools import cycle

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from ..forms import CommentForm, DiaryForm
from ..models import Diary
from ..views import (DiaryListView, DiaryDetailView, DiaryCreateView,
                     DiaryUpdateView, DiaryDeleteView)


class DiaryListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        user1 = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )
        user2 = get_user_model().objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2pass'  # -_-
        )
        user3 = get_user_model().objects.create_user(
            username='user3',
            email='user3@example.com',
            password='user3pass'  # -_-
        )
        cls.users = [user1, user2, user3]

        # Get profiles
        profile1 = Profile.objects.get(id=1)
        profile2 = Profile.objects.get(id=2)
        profile3 = Profile.objects.get(id=3)

        profile1.followers.add(profile3)

        cls.profiles = [profile1, profile2, profile3]
        cls.profile1 = profile1
        cls.profile2 = profile2
        cls.profile3 = profile3

    def create_diaries(self, num, profiles=None, feelings=None,
                       visibility_choices=None):
        if profiles is None:
            profiles = [
                DiaryListViewTest.profile1,
                DiaryListViewTest.profile2,
                DiaryListViewTest.profile3
            ]

        if feelings is None:
            feelings = [i[0] for i in Diary.FEELINGS_CHOICES]

        if visibility_choices is None:
            visibility_choices = [Diary.ALL_CHOICE]

        profiles_cycle = cycle(profiles)
        feelings_cycle = cycle(feelings)
        visibility_choices_cycle = cycle(visibility_choices)

        diaries = []
        for i in range(num):
            d = Diary(
                title=f'Diary N° {i + 1}',
                content=f'Content of diary N° {i + 1}',
                feeling=next(feelings_cycle),
                is_visible=next(visibility_choices_cycle),
                author=next(profiles_cycle)
            )
            d.save()
            diaries.append(d)
        return diaries

    def test_view_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryListView.as_view().__name__)

    def test_view_url_is_accessible_by_name(self):
        response = self.client.get(reverse('diaries:diary_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryListView.as_view().__name__)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('diaries:diary_list'))
        self.assertTemplateUsed(response, 'diaries/diary_list.html')

    def test_template_returns_correct_msg_if_no_diaries(self):
        response = self.client.get(reverse('diaries:diary_list'))
        self.assertContains(response, 'There is no diaries.')

    def test_template_does_not_returns_msg_if_diaries(self):
        self.create_diaries(num=1)
        response = self.client.get(reverse('diaries:diary_list'))
        self.assertNotContains(response, 'There is no diaries.')

    def test_diaries_are_paginated(self):
        self.create_diaries(num=10)
        response = self.client.get(reverse('diaries:diary_list'))
        self.assertIn('is_paginated', response.context)
        self.assertIn('page_obj', response.context)

    def test_each_page_contains_correct_number_of_diaries(self):
        self.create_diaries(num=20)
        response = self.client.get(reverse('diaries:diary_list'))  # page=1
        self.assertEqual(len(response.context['diaries']), 9)

        response = self.client.get(reverse('diaries:diary_list') + '?page=1')
        self.assertEqual(len(response.context['diaries']), 9)

        response = self.client.get(reverse('diaries:diary_list') + '?page=2')
        self.assertEqual(len(response.context['diaries']), 9)

        response = self.client.get(reverse('diaries:diary_list') + '?page=3')
        self.assertEqual(len(response.context['diaries']), 2)

    def test_each_rendered_page_contains_pagination_links(self):
        self.create_diaries(num=20)
        for i in range(1, 4):
            response = self.client.get(
                reverse('diaries:diary_list') + f'?page={i}')
            for j in range(1, 4):
                self.assertContains(response, f'href="?page={j}"')

    def test_unlogged_in_user_sees_all_diaries(self):
        self.create_diaries(num=3)
        response = self.client.get(reverse('diaries:diary_list'))
        authors = []
        for diary in response.context['diaries']:
            authors.append(diary.author)

        for profile in self.profiles:
            self.assertIn(profile, authors)

    def test_logged_in_user_sees_his_and_diaries_of_people_he_follows(self):
        self.create_diaries(num=3)

        self.client.login(username='user3', password='user3pass')
        # User 3 follows user 1
        response = self.client.get(reverse('diaries:diary_list'))
        authors = []
        for diary in response.context['diaries']:
            authors.append(diary.author)

        self.assertIn(self.profile1, authors)
        self.assertIn(self.profile3, authors)
        self.assertNotIn(self.profile2, authors)


class DiaryDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )
        get_user_model().objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2pass'  # -_-
        )

        # Get profiles
        cls.profile1 = Profile.objects.get(id=1)
        cls.profile2 = Profile.objects.get(id=2)
        cls.profiles = [cls.profile1, cls.profile2]

        cls.diary1 = Diary(
            title=f'Diary By profile1',
            content=f'Content of diary',
            feeling=Diary.EXCITED_FEELING,
            author=cls.profile1
        )
        cls.diary1.save()

        cls.diary1_detail_url = reverse(
            'diaries:diary_detail',
            kwargs={'diary_slug': DiaryDetailViewTest.diary1.slug}
        )

        cls.diary2 = Diary(
            title=f'Diary By profile2',
            content=f'Content of diary',
            feeling=Diary.EXCITED_FEELING,
            author=cls.profile2,
            is_visible=Diary.NO_ONE_CHOICE
        )
        cls.diary2.save()

        cls.diary2_detail_url = reverse(
            'diaries:diary_detail',
            kwargs={'diary_slug': DiaryDetailViewTest.diary2.slug}
        )

        cls.diary3 = Diary(
            title=f'Diary By profile2',
            content=f'Content of diary',
            feeling=Diary.EXCITED_FEELING,
            author=cls.profile2,
            is_commentable=Diary.NO_ONE_CHOICE
        )
        cls.diary3.save()

        cls.diary3_detail_url = reverse(
            'diaries:diary_detail',
            kwargs={'diary_slug': DiaryDetailViewTest.diary3.slug}
        )

    def test_view_url_is_accessible_by_name(self):
        response = self.client.get(DiaryDetailViewTest.diary1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryDetailView.as_view().__name__)

    def test_view_uses_correct_template(self):
        response = self.client.get(DiaryDetailViewTest.diary1_detail_url)
        self.assertTemplateUsed(response, 'diaries/diary_detail.html')

    def test_user_can_see_his_public_diary(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryDetailViewTest.diary1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['diary'], DiaryDetailViewTest.diary1)

    def test_user_can_see_public_diary_of_other_user(self):
        self.client.login(username='user2', password='user2pass')
        response = self.client.get(DiaryDetailViewTest.diary1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['diary'], DiaryDetailViewTest.diary1)

    def test_user_can_see_his_draft_diary(self):
        self.client.login(username='user2', password='user2pass')
        response = self.client.get(DiaryDetailViewTest.diary2_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['diary'], DiaryDetailViewTest.diary2)

    def test_user_cant_see_draft_diary_of_other_user(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryDetailViewTest.diary2_detail_url)
        self.assertEqual(response.status_code, 404)
        with self.assertRaises(KeyError):
            response.context['diary']

    def test_logged_in_user_can_see_comment_form_on_commentable_diary(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryDetailViewTest.diary1_detail_url)
        comment_url = reverse(
            'diaries:comment_create',
            args=[DiaryDetailViewTest.diary1.slug])
        self.assertContains(
            response,
            f'<form method="post" action="{comment_url}">'
        )
        self.assertIsInstance(response.context['comment_form'], CommentForm)

    def test_unlogged_in_user_can_see_comment_form_on_commentable_diary(self):
        response = self.client.get(DiaryDetailViewTest.diary1_detail_url)
        comment_url = reverse(
            'diaries:comment_create',
            args=[DiaryDetailViewTest.diary1.slug])
        self.assertNotContains(
            response,
            f'<form method="post" action="{comment_url}">'
        )
        self.assertEqual(response.context['comment_form'], None)

    def test_user_wont_see_comment_form_on_non_commentable_diary(self):
        self.client.login(username='user2', password='user2pass')
        response = self.client.get(DiaryDetailViewTest.diary3_detail_url)
        comment_url = reverse(
            'diaries:comment_create',
            args=[DiaryDetailViewTest.diary3.slug])
        self.assertNotContains(
            response,
            f'<form method="post" action="{comment_url}">'
        )
        self.assertEqual(response.context['comment_form'], None)
        self.assertContains(response, 'Comments are disabled for this diary.')

    def test_unlogged_user_wont_see_comment_form_non_commentable_diary(self):
        response = self.client.get(DiaryDetailViewTest.diary3_detail_url)
        comment_url = reverse(
            'diaries:comment_create',
            args=[DiaryDetailViewTest.diary3.slug])
        self.assertNotContains(
            response,
            f'<form method="post" action="{comment_url}">'
        )
        self.assertEqual(response.context['comment_form'], None)
        self.assertContains(response, 'Comments are disabled for this diary.')


class DiaryCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        cls.profile1 = Profile.objects.get(id=1)

        cls.CREATE_URL = reverse('diaries:diary_create')

    def test_view_exists_at_desired_location(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get('/create')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryCreateView.as_view().__name__)

    def test_view_url_is_accessible_by_name(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryCreateViewTest.CREATE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryCreateView.as_view().__name__)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(reverse('diaries:diary_create'))
        self.assertTemplateUsed(response, 'diaries/diary_create.html')

    def test_unlogged_in_user_gets_redirected(self):
        response = self.client.get(DiaryCreateViewTest.CREATE_URL)
        expected_url = ''.join((
            f'{reverse(settings.LOGIN_URL)}',
            f'?next={DiaryCreateViewTest.CREATE_URL}'))
        self.assertRedirects(response, expected_url=expected_url)

    def test_response_contains_diary_create_form(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryCreateViewTest.CREATE_URL)
        form_tag = '<form method="post" '
        form_tag += f'action="{DiaryCreateViewTest.CREATE_URL}" '
        form_tag += 'enctype="multipart/form-data" class="browser-default">'

        self.assertIsInstance(response.context['form'], DiaryForm)
        self.assertContains(response, form_tag)

    def test_diary_is_created_successfly_with_minumum_data(self):
        self.client.login(username='user1', password='user1pass')
        payload = {
            'title': 'Test diary',
            'content': 'Just some content',
        }
        response = self.client.post(
            DiaryCreateViewTest.CREATE_URL,
            data=payload)
        self.assertEqual(Diary.objects.count(), 1)

        diary = Diary.objects.first()

        self.assertRedirects(response, diary.get_absolute_url())
        self.assertEqual(diary.author, DiaryCreateViewTest.profile1)

    def test_diary_is_created_successfly_with_all_data(self):
        self.client.login(username='user1', password='user1pass')
        payload = {
            'title': 'Test diary',
            'content': 'Just some content',
            'is_visible': Diary.NO_ONE_CHOICE,
            'is_commentable': Diary.ALL_CHOICE,
            'feeling': Diary.SATISFIED_FEELING,
        }
        response = self.client.post(
            DiaryCreateViewTest.CREATE_URL,
            data=payload)
        self.assertEqual(Diary.objects.count(), 1)

        diary = Diary.objects.first()

        self.assertRedirects(response, diary.get_absolute_url())
        self.assertEqual(diary.author, DiaryCreateViewTest.profile1)

    def test_diary_is_not_created_if_no_data_is_submited(self):
        self.client.login(username='user1', password='user1pass')
        payload = {
            'title': '',
            'content': '',
        }
        response = self.client.post(
            DiaryCreateViewTest.CREATE_URL,
            data=payload)

        self.assertEqual(Diary.objects.count(), 0)
        self.assertTrue(response.context['form'].errors)


class DiaryUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        cls.profile = Profile.objects.get(id=1)

        cls.diary = Diary.objects.create(
            title='A test diary',
            content='test content',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryUpdateViewTest.profile
        )

        cls.UPDATE_URL = reverse('diaries:diary_update', args=['a-test-diary'])

    def test_view_exists_at_desired_location(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get('/diary/a-test-diary/update')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryUpdateView.as_view().__name__)

    def test_view_url_is_accessible_by_name(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryUpdateViewTest.UPDATE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryUpdateView.as_view().__name__)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryUpdateViewTest.UPDATE_URL)
        self.assertTemplateUsed(response, 'diaries/diary_update.html')

    def test_response_contains_diary_update_form(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryUpdateViewTest.UPDATE_URL)
        form_tag = '<form method="post" '
        form_tag += f'action="{DiaryUpdateViewTest.UPDATE_URL}" '
        form_tag += 'enctype="multipart/form-data">'

        self.assertIsInstance(response.context['form'], DiaryForm)
        self.assertIsInstance(response.context['form'].instance, Diary)
        self.assertContains(response, form_tag)

    def test_unlogged_in_user_gets_redirected(self):
        response = self.client.get(DiaryUpdateViewTest.UPDATE_URL)
        expected_url = ''.join((
            f'{reverse(settings.LOGIN_URL)}',
            f'?next={DiaryUpdateViewTest.UPDATE_URL}'))
        self.assertRedirects(response, expected_url=expected_url)

    def test_unlogged_in_user_cant_update_via_post(self):
        payload = {
            'title': 'A test diary updated',
            'content': 'test content updated',
            'is_visible': Diary.NO_ONE_CHOICE,
            'is_commentable': Diary.NO_ONE_CHOICE,
            'feeling': Diary.TIRED_FEELING
        }
        response = self.client.post(
            DiaryUpdateViewTest.UPDATE_URL,
            data=payload)
        expected_url = ''.join((
            f'{reverse(settings.LOGIN_URL)}',
            f'?next={DiaryUpdateViewTest.UPDATE_URL}'))
        self.assertRedirects(response, expected_url=expected_url)

    def test_diary_is_updated_successfly(self):
        self.client.login(username='user1', password='user1pass')
        payload = {
            'title': 'A test diary updated',
            'content': 'test content updated',
            'is_visible': Diary.NO_ONE_CHOICE,
            'is_commentable': Diary.NO_ONE_CHOICE,
            'feeling': Diary.TIRED_FEELING
        }
        response = self.client.post(
            DiaryUpdateViewTest.UPDATE_URL,
            data=payload)
        self.assertEqual(Diary.objects.count(), 1)

        diary = Diary.objects.first()

        self.assertRedirects(response, diary.get_absolute_url())
        self.assertEqual(diary.author, DiaryUpdateViewTest.profile)

        for key, value in payload.items():
            self.assertEqual(getattr(diary, key), value)


class DiaryDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        cls.profile = Profile.objects.get(id=1)

        cls.diary = Diary.objects.create(
            title='A test diary',
            content='test content',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryDeleteViewTest.profile
        )

        cls.DELETE_URL = reverse('diaries:diary_delete', args=['a-test-diary'])

    def test_view_exists_at_desired_location(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get('/diary/a-test-diary/delete')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryDeleteView.as_view().__name__)

    def test_view_url_is_accessible_by_name(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryDeleteViewTest.DELETE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__,
                         DiaryDeleteView.as_view().__name__)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryDeleteViewTest.DELETE_URL)
        self.assertTemplateUsed(response, 'diaries/diary_delete.html')

    def test_response_contains_diary_delete_form(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(DiaryDeleteViewTest.DELETE_URL)
        form_tag = '<form method="post" '
        form_tag += f'action="{DiaryDeleteViewTest.DELETE_URL}">'

        self.assertContains(response, form_tag)

    def test_unlogged_in_user_gets_redirected(self):
        response = self.client.get(DiaryDeleteViewTest.DELETE_URL)
        expected_url = ''.join((
            f'{reverse(settings.LOGIN_URL)}',
            f'?next={DiaryDeleteViewTest.DELETE_URL}'))
        self.assertRedirects(response, expected_url=expected_url)

    def test_diary_is_deleted_successfly(self):
        self.client.login(username='user1', password='user1pass')
        response = self.client.post(DiaryDeleteViewTest.DELETE_URL)

        expected_url = reverse('diaries:diary_list')
        self.assertRedirects(response, expected_url=expected_url)
        self.assertEqual(Diary.objects.count(), 0)
