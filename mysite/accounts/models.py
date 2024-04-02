from django.contrib.auth.models import User
from django.db import models


def user_directory_path(instance, filename):
    return 'users/user_{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    agreement_accepted = models.BooleanField(default=False)