from django.contrib import admin

from .models import Diary, DiaryLike, Comment, CommentLike


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
	list_display = (
		'title', 
		'slug', 
		'author', 
		'created_on', 
		'updated_on', 
		'is_visible', 
		'is_commentable'
		)

admin.site.register(DiaryLike)
admin.site.register(Comment)
admin.site.register(CommentLike)