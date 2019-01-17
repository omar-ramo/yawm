from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Diary, Comment


class DiaryForm(forms.ModelForm):
	class Meta:
		model = Diary
		fields = [
			'title',
			'content',
			'image',
			'is_visible',
			'is_commentable',
			'feeling',
			]
		# widgets = {
		# 	'content': CKEditorUploadingWidget()
		# }

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['content']