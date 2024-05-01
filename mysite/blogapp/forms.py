from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Author, Article


class AuthorCreateForm(UserCreationForm):
    bio = forms.CharField(max_length=500)

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "bio"]


class ArticleForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=Author.objects.all())

    class Meta:
        model = Article
        fields = ['title', 'content', 'author', 'category', 'tags']
