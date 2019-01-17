from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, DetailView, DeleteView, UpdateView, CreateView
from django.urls import reverse

from .forms import DiaryForm, CommentForm
from .models import Diary, DiaryLike, Comment, CommentLike


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
				followed_profiles_diaries = Diary.objects.from_followed_profiles(self.request.user.profile).order_by()
				current_profile_diaries = Diary.objects.with_likes_and_comments_count().filter(author=self.request.user.profile).order_by()
				qs = followed_profiles_diaries.union(current_profile_diaries).order_by('-created_on')
			else:
				qs = self.model.objects.with_likes_and_comments_count()
		return qs

class DiaryDetailView(DetailView):
	model = Diary
	template_name = 'diaries/diary_detail.html'
	context_object_name = 'diary'
	slug_field = 'slug'
	slug_url_kwarg = 'diary_slug'

	def get_queryset(self):
		qs = self.model.objects.with_likes_and_comments_count()
		return qs

	def get_context_data(self, **kwargs):
		cx =  super(DiaryDetailView, self).get_context_data(**kwargs)

		comment_form = CommentForm()
		cx['comment_form'] = comment_form

		current_user_likes_diary = False
		if self.request.user.is_authenticated:
			if self.request.user.profile in self.object.likes.all():
				current_user_likes_diary = True
		cx['current_user_likes_diary'] = current_user_likes_diary
		print(cx)

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
		obj = get_object_or_404(self.model, slug=self.kwargs[self.slug_url_kwarg])
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
		obj = get_object_or_404(self.model, slug=self.kwargs[self.slug_url_kwarg])
		if self.request.user.profile == obj.author:
			return obj
		raise Http404()

class DiaryLikeView(LoginRequiredMixin, View):
	def get(self, request, diary_slug):
		diary = get_object_or_404(Diary, slug=diary_slug)
		return redirect(diary)

	def post(self, request, diary_slug):
		diary = get_object_or_404(Diary, slug=diary_slug)
		# if request.user.profile in diary.likes.all():
		# 	diary.likes.remove(request.user.profile)
		# else:
		# 	diary.likes.add(request.user.profile)
		dl, created = DiaryLike.objects.get_or_create(diary=diary, user=request.user.profile)
		if not created:
			dl.delete()
		return redirect(diary)


class CommentCreateView(LoginRequiredMixin, View):
	form_class = CommentForm

	def get(self, *args, **kwargs):
		diary = get_object_or_404(Diary, slug=self.kwargs['diary_slug'])
		return redirect(diary)

	def post(self, *args, **kwargs):
		diary = get_object_or_404(Diary, slug=self.kwargs['diary_slug'], is_visible=True, is_commentable=True)
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

	def get_success_url(self):
		diary = get_object_or_404(Diary, slug=self.kwargs[self.diary_slug_url_kwarg])
		return diary.get_absolute_url()

	def get_object(self):
		obj = get_object_or_404(self.model, id=self.kwargs[self.comment_id_url_kwarg])
		if self.request.user.profile == obj.author:
			return obj
		raise Http404()