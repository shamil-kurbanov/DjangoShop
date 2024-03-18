from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from sqlalchemy.testing.pickleable import User


# class UserBioForm(forms.ModelForm):
#    class Meta:
#       model = User

class UserBioForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100, widget=forms.TextInput)
    age = forms.IntegerField(label="Your Age", min_value=1, max_value=120)
    bio = forms.CharField(label="Biography", max_length=400, widget=forms.Textarea)


def validate_file_name(file: InMemoryUploadedFile) -> None:
    if "virus" in file.name:
        raise ValidationError("filename should not contain `virus`")


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_file_name])
