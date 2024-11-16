from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserFile, Folder
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


def validate_file_size(file):
    max_size_mb = 100  # Set this according to your requirements
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"The file size exceeds the maximum limit of {max_size_mb} MB. Please choose a smaller file.")


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class FileRenameForm(forms.ModelForm):
    new_name = forms.CharField(max_length=255)

    class Meta:
        model = UserFile
        fields = ['new_name']


class FolderCreateForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder']


class FileUploadForm(forms.ModelForm):
    folder = forms.ModelChoiceField(queryset=Folder.objects.none(), required=False, empty_label="--- Select Folder ---")

    class Meta:
        model = UserFile
        fields = ['file', 'folder']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['folder'].queryset = Folder.objects.filter(user=user)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        validate_file_size(file)  # Validate the file size
        return file


class MoveFileForm(forms.Form):
    target_folder = forms.ModelChoiceField(queryset=Folder.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['target_folder'].queryset = Folder.objects.filter(user=user)


class CopyFileForm(forms.Form):
    target_folder = forms.ModelChoiceField(queryset=Folder.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['target_folder'].queryset = Folder.objects.filter(user=user)
