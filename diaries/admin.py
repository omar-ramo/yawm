from django.contrib import admin

from .models import Diary, DiaryLike, Comment, CommentLike


admin.site.register(Diary)
admin.site.register(DiaryLike)
admin.site.register(Comment)
admin.site.register(CommentLike)