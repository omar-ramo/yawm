from django.urls import path

from .import views


app_name = 'diaries_api'
urlpatterns = [
    path('', views.DiaryListCreateAPIView.as_view(), name='diary_list'),
    path(
        '<slug:diary_slug>',
        views.DiaryRetrieveUpdateDestroyAPIView.as_view(),
        name='diary_detail'),
]
