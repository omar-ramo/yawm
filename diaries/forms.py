from django import forms
from bleach.sanitizer import Cleaner

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
        cleaner = Cleaner(
            tags=[
                'p', 'u', 's', 'i', 'b', 'a', 'sub', 'sup', 'img', 'div',
                'ul', 'li', 'ol', 'em', 'strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'pre', 'address', 'caption'
            ],
            attributes={
                'a':['href', 'target'],
                'img':['src', 'style', 'alt'],
            },
            styles=['height', 'width'],
            protocols=['http', 'https', 'mailto']
        )
        content = cleaner.clean(content)
        return content


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
