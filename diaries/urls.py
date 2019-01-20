from django.urls import path, include

from . import views

app_name='diaries'

urlpatterns = [
    path('', views.DiaryListView.as_view(), name='diary_list'),
    path(
        'popular', 
        views.DiaryListView.as_view(
            order_by='popularity', 
            template_name='diaries/diary_list_popular.html'
            ), 
        name='popular_diary_list'),
    path(
        'discover', 
        views.DiaryListView.as_view(
            order_by='discover', 
            template_name='diaries/diary_list_discover.html'
            ), 
        name='discover_diary_list'),
    path('diary/<slug:diary_slug>/', include([
    	path('', views.DiaryDetailView.as_view(), name='diary_detail'),
        path('like', views.DiaryLikeView.as_view(), name='diary_like'),
        path('update', views.DiaryUpdateView.as_view(), name='diary_update'),
    	path('delete', views.DiaryDeleteView.as_view(), name='diary_delete'),
    	#Comments
    	path(
            'comment/create', 
            views.CommentCreateView.as_view(), 
            name='comment_create'
            ),
    	path(
            'comment/<int:comment_id>/delete', 
            views.CommentDeleteView.as_view(), 
            name='comment_delete'
            ),
    	])
    ),
    path('create', views.DiaryCreateView.as_view(), name='diary_create'),
    path('search', views.SearchView.as_view(), name='search'),
]
