from django.contrib.auth.models import Group, User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.mixins import (ListModelMixin,
                                   RetrieveModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin,
                                   CreateModelMixin)

from .serializers import GroupSerializer, UserSerializer, BookSerializer
from .models import Book


@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello World!"})


# class GroupsListView(APIView):
#    def get(self, request: Request) -> Response:
#        groups = Group.objects.all()
#        data = [group.name for group in groups]
#        return Response({"groups": data})

# class GroupsListView(APIView):
#    def get(self, request: Request) -> Response:
#        groups = Group.objects.all()
#        serialized_groups = GroupSerializer(groups, many=True)
#        return Response(serialized_groups.data)

# class GroupsListView(ListModelMixin, GenericAPIView):
#    queryset = Group.objects.all()
#    serializer_class = GroupSerializer
#
#    def get(self, request: Request) -> Response:
#        return self.list(request)

class GroupsListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupRetrieveUpdateDestroy(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class BookListCreate(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class UsersListView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer