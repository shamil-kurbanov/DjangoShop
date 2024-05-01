from django.contrib.auth.models import Group, User
from rest_framework import serializers, viewsets
from .models import Book


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = 'pk', 'name'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        extra_kwargs = {'password': {'write_only': True}}

