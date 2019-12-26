from django.urls import path, include

from . import views

app_name = 'accounts'

urlpatterns = [
    path('profiles', views.ProfileTopListView.as_view(), name='profile_list'),
    path('<str:username>/', include([
         path(
             '',
             views.ProfileDetailView.as_view(),
             name='profile_detail'),
         path(
             'update',
             views.ProfileUpdateView.as_view(),
             name='profile_update'),
         path(
             'follow',
             views.ProfileFollowView.as_view(),
             name='profile_follow'),
         path(
             'followers',
             views.ProfileFollowersListView.as_view(),
             name='profile_followers_list'),
         path(
             'following',
             views.ProfileFollowingListView.as_view(),
             name='profile_following_list')]))
]
