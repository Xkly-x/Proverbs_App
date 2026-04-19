from django import forms
from .models import Profile, Proverb, Comment

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

class ProverbSubmitForm(forms.ModelForm):
    class Meta:
        model = Proverb
        fields = ['text', 'meaning', 'categories', 'difficulty']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'meaning': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Напишите комментарий...'
            })
        }