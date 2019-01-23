from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
	View, 
	ListView, 
	DetailView, 
	DeleteView, 
	UpdateView, 
	CreateView
	)
from django.urls import reverse
from notifications.views import NotificationViewList
from notifications.models import Notification

from .forms import DiaryForm, CommentForm
from .models import Diary, DiaryLike, Comment, CommentLike
from accounts.models import Profile


DIARIES_PER_PAGE = 9

class DiaryListView(ListView):
	model = Diary
	paginate_by = DIARIES_PER_PAGE
	template_name = 'diaries/diary_list.html'
	context_object_name = 'diaries'
	order_by = None

	def get_queryset(self):
		order_by = self.order_by
		if order_by == 'popularity':
			qs = self.model.objects.popular()
		elif order_by == 'discover':
			qs = self.model.objects.with_likes_and_comments_count()
		else:
			if self.request.user.is_authenticated:
				# User will only see the diaries of people he follow + his own
				# I will use .active(self.request.user) here because the
				# Resulting qs of .union() doesn't allow oher operations
				# other than: count, order_by, values,values_list
				followed_profiles_diaries = Diary.objects\
					.from_followed_profiles(self.request.user.profile).order_by()\
					.active(self.request.user)

				current_profile_diaries = Diary.objects\
					.with_likes_and_comments_count().filter(
						author=self.request.user.profile
						).order_by().active(self.request.user)

				qs = followed_profiles_diaries.union(current_profile_diaries)
				qs = qs.order_by('-created_on')
			else:
				qs = self.model.objects.with_likes_and_comments_count()
		qs = qs.active(self.request.user)
		return qs
		

class DiaryDetailView(DetailView):
	model = Diary
	template_name = 'diaries/diary_detail.html'
	context_object_name = 'diary'
	slug_field = 'slug'
	slug_url_kwarg = 'diary_slug'

	def get_object(self):
		qs = self.model.objects.with_likes_and_comments_count()
		if self.request.user.is_authenticated:
			qs = qs.filter(
				slug=self.kwargs[self.slug_url_kwarg]
				)
		else:
			qs = qs.filter(
				slug=self.kwargs[self.slug_url_kwarg]
				)
		qs = qs.active(self.request.user)
		obj = qs.first()
		if obj == None:
			raise Http404()
		return obj

	def get_context_data(self, **kwargs):
		cx =  super(DiaryDetailView, self).get_context_data(**kwargs)

		comment_form = None
		if self.object.is_commentable == Diary.ALL_CHOICE:
			comment_form = CommentForm()
		cx['comment_form'] = comment_form

		return cx

class DiaryCreateView(LoginRequiredMixin, CreateView):
	form_class = DiaryForm
	template_name = 'diaries/diary_create.html'
	context_object_name = 'diary'

	def get_success_url(self):
		return self.object.get_absolute_url()

	def form_valid(self, form):
		form.instance.author = self.request.user.profile
		return super().form_valid(form)

class DiaryUpdateView(LoginRequiredMixin, UpdateView):
	model = Diary
	form_class = DiaryForm
	template_name = 'diaries/diary_update.html'
	slug_url_kwarg = 'diary_slug'
	context_object_name = 'diary'

	def get_success_url(self):
		return self.object.get_absolute_url()

	def get_object(self):
		obj = get_object_or_404(
			self.model, 
			slug=self.kwargs[self.slug_url_kwarg]
			)
		if self.request.user.profile == obj.author:
			return obj
		raise Http404()

class DiaryDeleteView(LoginRequiredMixin, DeleteView):
	model = Diary
	template_name = 'diaries/diary_delete.html'
	slug_field = 'slug'
	slug_url_kwarg = 'diary_slug'

	def get_success_url(self):
		return reverse('diaries:diary_list')

	def get_object(self):
		obj = get_object_or_404(
			self.model, 
			slug=self.kwargs[self.slug_url_kwarg]
			)
		if self.request.user.profile == obj.author:
			return obj
		raise Http404()

class DiaryLikeView(LoginRequiredMixin, View):
	def get(self, request, diary_slug):
		diary = get_object_or_404(Diary, slug=diary_slug)
		return redirect(diary)

	def post(self, request, diary_slug):
		diary = get_object_or_404(
			Diary, 
			slug=diary_slug, 
			is_visible=Diary.ALL_CHOICE)

		dl, created = DiaryLike.objects.get_or_create(
			diary=diary, 
			user=request.user.profile
			)
		if not created:
			dl.delete()
		return redirect(diary)


class CommentCreateView(LoginRequiredMixin, View):
	form_class = CommentForm

	def get(self, *args, **kwargs):
		diary = get_object_or_404(
			Diary, 
			slug=self.kwargs['diary_slug'], 
			is_visible=Diary.ALL_CHOICE
			)
		return redirect(diary)

	def post(self, *args, **kwargs):
		diary = get_object_or_404(
			Diary, 
			slug=self.kwargs['diary_slug'], 
			is_visible=Diary.ALL_CHOICE, 
			is_commentable=Diary.ALL_CHOICE
			)
		comment_form = CommentForm(self.request.POST)
		if comment_form.is_valid():
			new_comment = comment_form.save(commit=False)
			new_comment.author = self.request.user.profile
			new_comment.diary = diary
			new_comment.save()
			return redirect(diary)
		else:
			return redirect(diary)

class CommentDeleteView(LoginRequiredMixin, DeleteView):
	model = Comment
	template_name = 'diaries/comment_delete.html'
	diary_slug_url_kwarg = 'diary_slug'
	comment_id_url_kwarg = 'comment_id'

	def get_object(self):
		obj = get_object_or_404(
			self.model, 
			id=self.kwargs[self.comment_id_url_kwarg], 
			diary__is_visible=Diary.ALL_CHOICE
			)
		if self.request.user.profile == obj.author:
			return obj
		raise Http404()

	def get_success_url(self):
		diary = get_object_or_404(
			Diary, 
			slug=self.kwargs[self.diary_slug_url_kwarg]
			)
		return diary.get_absolute_url()

class SearchView(View):
	def get(self, request):
		q = request.GET.get('q', '')

		diaries = Diary.objects.with_likes_and_comments_count().active(self.request.user)
		diaries = diaries.filter(title__contains=q).distinct()[:9]

		profiles = Profile.objects.filter(
			Q(name__contains=q) |
			Q(user__username__contains=q) |
			Q(description__contains=q)
			).distinct()[:12]

		context = {
			'diaries': diaries,
			'profiles': profiles,
			'q': q
		}
		return render(request, 'diaries/search.html', context)

class NotificationListView(LoginRequiredMixin, NotificationViewList):
	template_name='diaries/notification_list.html'
	paginate_by = 10

	def get_queryset(self):
		qs = Notification.objects.filter(recipient=self.request.user)
		qs = qs.active()
		return qs

