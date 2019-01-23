from django.conf import settings
from django.db import models
from django.db.models import Count, F
from django.db.models.signals import post_save
from django.urls import reverse

from core.utils import get_image_upload_path, generate_random_string


class ProfileQuerySet(models.QuerySet):
	def with_diaries_followers_count(self):
		return self.annotate(
			written_diaries_count=Count('written_diaries', distinct=True),
			followers_count=Count('followers', distinct=True),
			)

	def top(self):
		qs = self.with_diaries_followers_count()
		qs = qs.annotate(
				interactions=
					F('written_diaries_count')
					+ F('followers_count')
				).order_by('-interactions')
		return qs

class Profile(models.Model):
	MALE = 'm'
	FEMALE = 'f'
	NOT_SPECIFIED = 'n'
	GENDER_CHOICES = (
		(MALE, 'Male'),
		(FEMALE, 'Female'),
		(NOT_SPECIFIED, 'I prefer not to say')
		)

	name = models.CharField(
		help_text='If you don\'t provide one. your username will be used',
		max_length=63,
		blank=True
		)
	followers = models.ManyToManyField(
		'self', 
		related_name='followed_profiles', 
		symmetrical=False, 
		blank=True
		)
	image = models.ImageField(
		upload_to=get_image_upload_path,
		null=True,
		blank=True
		)
	description = models.CharField(
		max_length=255, 
		null=True, 
		blank=True,
		help_text='Describe yourself in less than 255 character.'
		)
	gender = models.CharField(
		max_length=1,
		choices=GENDER_CHOICES,
		default=NOT_SPECIFIED
		)

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL, 
		on_delete=models.CASCADE, 
		related_name='profile'
		)

	objects = ProfileQuerySet.as_manager()


	def __str__(self):
		return '{}'.format(self.name)

	def get_absolute_url(self):
		return reverse('accounts:profile_detail', args=[self.user.username])

	def save(self, *args, **kwargs):
		if not self.name:
			self.name = self.user.username
		return super(Profile, self).save(*args, **kwargs)

	@property
	def visible_written_diaries_count(self):
		return self.written_diaries.filter(is_visible='all').count()
	


def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)