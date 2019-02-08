from django import forms
import bleach
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

	def clean_content(self):
		content = self.cleaned_data['content']
		content = bleach.clean(content)
		content = bleach.linkify(content)
		return content


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['content']
