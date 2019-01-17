from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('name', 'image', 'gender', 'description')
		widgets = {
			'description': forms.Textarea()
		}