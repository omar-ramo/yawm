from django.contrib.auth.views import LogoutView
from django.urls import path, include

from . import views

app_name = 'accounts'

urlpatterns = [
    path('logout', LogoutView.as_view(), name='logout'),
    path('login', views.LoginView.as_view(), name='login'),
    path('signup', views.SignupView.as_view(), name='signup'),
    path('profiles', views.ProfileListView.as_view(), name='profile_list'),
    path('<str:username>/',
         include([
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
         ]
         )
         )
]
