from itertools import cycle

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from ..models import Diary, DiaryLike, Comment
from ..views import DiaryListView


class DiaryListViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		#Create users
		user1 = get_user_model().objects.create_user(
			username='user1',
			email='user1@example.com',
			password='user1pass' # -_-
			)
		user2 = get_user_model().objects.create_user(
			username='user2',
			email='user2@example.com',
			password='user2pass' # -_-
			)
		user3 = get_user_model().objects.create_user(
			username='user3',
			email='user3@example.com',
			password='user3pass' # -_-
			)
		cls.users = [user1, user2, user3]

		# Get profiles
		profile1 = Profile.objects.get(id=1)
		cls.profile2 = Profile.objects.get(id=2)
		profile3 = Profile.objects.get(id=3)
		profile1.followers.add(profile3)
		cls.profile1 = profile1
		cls.profile3 = profile3
		cls.profiles = [cls.profile1, cls.profile2, cls.profile3]

		# Create diaries
		num_of_diaries = 20

		profiles_cycle = cycle([cls.profile1, cls.profile2, cls.profile3])
		for i in range(1, num_of_diaries+1):
			d = Diary(
				title=f'Diary N° {i}',
				content=f'Content of diary N° {i}',
				feeling=Diary.EXCITED_FEELING,
				author=next(profiles_cycle)
				)
			d.save()
		cls.diaries = Diary.objects.all()

	def test_view_exists_at_desired_location(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func.__name__, DiaryListView.as_view().__name__)

	def test_view_url_is_accessible_by_name(self):
		response = self.client.get(reverse('diaries:diary_list'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func.__name__, DiaryListView.as_view().__name__)

	def test_view_uses_correct_template(self):
		response = self.client.get(reverse('diaries:diary_list'))
		self.assertTemplateUsed(response, 'diaries/diary_list.html')

	def test_diaries_are_paginated(self):
		response = self.client.get(reverse('diaries:diary_list'))
		self.assertIn('is_paginated', response.context)
		self.assertIn('page_obj', response.context)
	
	def test_each_page_contains_correct_number_of_diaries(self):
		response = self.client.get(reverse('diaries:diary_list')) # page=1
		self.assertEqual(len(response.context['diaries']), 9)
		
		response = self.client.get(reverse('diaries:diary_list') + '?page=1')
		self.assertEqual(len(response.context['diaries']), 9)
		
		response = self.client.get(reverse('diaries:diary_list') + '?page=2')
		self.assertEqual(len(response.context['diaries']), 9)
		
		response = self.client.get(reverse('diaries:diary_list') + '?page=3')
		self.assertEqual(len(response.context['diaries']), 2)
	
	def test_rendered_content_contains_pagination_links(self):
		for i in range(1, 4):
			response = self.client.get(reverse('diaries:diary_list') + f'?page={i}')
			for j in range(1, 4):
				self.assertContains(response, f'href="?page={j}"')

	def test_unlogged_in_user_sees_all_diaries(self):
		response = self.client.get(reverse('diaries:diary_list'))
		authors = []
		for diary in response.context['diaries']:
			authors.append(diary.author)

		for profile in self.profiles:
			self.assertIn(profile, authors)

	def test_logged_in_user_sees_diaries_of_people_he_follows_and_his_own(
			self):
		self.client.login(username='user3', password='user3pass')
		response = self.client.get(reverse('diaries:diary_list'))
		authors = []
		for diary in response.context['diaries']:
			authors.append(diary.author)

		self.assertIn(self.profile1, authors)
		self.assertIn(self.profile3, authors)
		self.assertNotIn(self.profile2, authors)