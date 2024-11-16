# cloud_drive_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


"""
class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='user_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True, related_name='files')

    def __str__(self):
        return self.file_name
"""

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    file = models.FileField(upload_to='user_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)  # New field for last modification time
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()

    def __str__(self):
        return self.file_name


class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')

    def __str__(self):
        return self.name