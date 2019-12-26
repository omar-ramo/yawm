from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    View,
    DetailView,
    ListView,
    UpdateView
)
from notifications.signals import notify

from .forms import ProfileForm
from .models import Profile


class ProfileListBaseView(LoginRequiredMixin, ListView):
    template_name = 'accounts/profile_list.html'
    model = Profile
    paginate_by = 12
    context_object_name = 'profiles'


class ProfileTopListView(ProfileListBaseView):

    extra_context = {'title': 'People worth following'}

    def get_queryset(self):
        return self.model.objects.top()


class ProfileFollowersListView(ProfileListBaseView):

    def get_context_data(self, *args, **kwargs):
        cx = super().get_context_data(*args, **kwargs)
        username = self.kwargs.get('username')
        cx['title'] = 'People that follow {}'.format(username)
        return cx

    def get_queryset(self):
        username = self.kwargs.get('username')
        profile = get_object_or_404(self.model, user__username=username)

        followers = profile.followers.all().with_diaries_followers_count()
        return followers


class ProfileFollowingListView(ProfileListBaseView):

    def get_context_data(self, *args, **kwargs):
        cx = super().get_context_data(*args, **kwargs)
        username = self.kwargs.get('username')
        cx['title'] = 'People {} follows'.format(username)
        return cx

    def get_queryset(self):
        username = self.kwargs.get('username')
        profile = get_object_or_404(self.model, user__username=username)

        followed_profiles = profile.followed_profiles.all()\
            .with_diaries_followers_count()

        return followed_profiles


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    slug_url_kwarg = 'username'
    template_name = 'accounts/profile_update.html'

    def get_object(self):
        obj = get_object_or_404(
            self.model,
            user__username=self.kwargs[self.slug_url_kwarg]
        )
        if not obj == self.request.user.profile:
            raise Http404
        return obj


class ProfileDetailView(DetailView):
    template_name = 'accounts/profile_detail.html'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_object(self):
        obj = Profile.objects.with_diaries_followers_count().filter(
            user__username=self.kwargs[self.slug_url_kwarg]
        )
        if not obj:
            raise Http404
        return obj.first()

    def get_context_data(self, *args, **kwargs):
        cx = super().get_context_data(*args, **kwargs)
        cx['diaries'] = self.object.written_diaries.active(self.request.user)
        return cx


class ProfileFollowView(LoginRequiredMixin, View):
    def get(self, request, username):
        profile = get_object_or_404(Profile, user__username=username)
        return redirect(profile)

    def post(self, request, username):
        profile = get_object_or_404(Profile, user__username=username)
        current_profile = request.user.profile

        if profile != current_profile:
            if current_profile in profile.followers.all():
                profile.followers.remove(current_profile)
            else:
                profile.followers.add(current_profile)
                notify.send(
                    sender=current_profile,
                    recipient=profile.user,
                    verb='Started following you'
                )
            profile.save()
            return redirect(profile)
        return redirect(profile)
