from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Diary
from accounts.models import Profile


class DiaryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass'  # -_-
        )

        cls.profile = Profile.objects.get(id=1)

    def test_diary_is_assigned_a_slug_on_creation(self):
        diary = Diary.objects.create(
            title='A test diary',
            content='test content',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryModelTest.profile)

        self.assertEqual(diary.slug, 'a-test-diary')

        second_diary = Diary.objects.create(
            title='A test diary',
            content='test content',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryModelTest.profile)

        duplicate_slug_regex = r'a\-test\-diary\-[a-zA-Z0-9_-]{10}'
        self.assertRegex(second_diary.slug, duplicate_slug_regex)

    def test_diary_is_assigned_a_unicode_slug_on_creation(self):
        diary = Diary.objects.create(
            title='يومية للاختبار',
            content='test content',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryModelTest.profile)

        self.assertEqual(diary.slug, 'يومية-للاختبار')

        second_diary = Diary.objects.create(
            title='يومية للاختبار',
            content='test content',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryModelTest.profile)

        duplicate_slug_regex = r'يومية-للاختبار\-[a-zA-Z0-9_-]{10}'
        self.assertRegex(second_diary.slug, duplicate_slug_regex)

    def test_diary_is_assigned_plain_text_description_on_creation(self):
        diary = Diary.objects.create(
            title='A test diary',
            content='<p>test <i>cont<span>ent</span></i></p><p/><div>',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryModelTest.profile)
        self.assertEqual(diary.description, 'test content')

    def test_get_absolute_url(self):
        diary = Diary.objects.create(
            title='A test diary',
            content='test content',
            is_visible=Diary.ALL_CHOICE,
            is_commentable=Diary.ALL_CHOICE,
            feeling=Diary.EXCITED_FEELING,
            author=DiaryModelTest.profile)

        expected_url = '/diary/a-test-diary/'
        self.assertEqual(diary.get_absolute_url(), expected_url)
