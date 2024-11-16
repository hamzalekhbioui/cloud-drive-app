from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserFile, Folder
from .forms import FileUploadForm,FileRenameForm, FolderCreateForm, MoveFileForm, CopyFileForm 
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Sum
import datetime
from django.db import models 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
from django.conf import settings
from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404
from .models import UserFile



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Successfully logged in.")
                return redirect('file_explorer')  # Ensure this redirects to the file explorer
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log in the user after registration
            messages.success(request, "Registration successful. Welcome!")
            return redirect('file_explorer')  # Redirect to file explorer after registration
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})


@login_required
def account_info_view(request):
    file_categories = {
        'Images': ['jpg', 'jpeg', 'png', 'gif'],
        'Documents': ['pdf', 'doc', 'docx', 'txt'],
        'Videos': ['mp4', 'avi', 'mov'],
        'Source Code': ['py', 'js', 'html', 'css'],
        'Others': []
    }

    category_usage = {category: 0 for category in file_categories}
    user_files = UserFile.objects.filter(user=request.user)
    for file in user_files:
        extension = file.file_name.split('.')[-1].lower()
        found_category = False
        for category, extensions in file_categories.items():
            if extension in extensions:
                category_usage[category] += file.file_size
                found_category = True
                break
        if not found_category:
            category_usage['Others'] += file.file_size

    fig, ax = plt.subplots()
    labels = list(category_usage.keys())
    sizes = list(category_usage.values())
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png).decode('utf-8')
    buffer.close()

    return render(request, 'account_info.html', {
        'graphic': graphic,
        'category_usage': category_usage,
    })


@login_required
def rename_file_view(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    if request.method == 'POST':
        form = FileRenameForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['new_name']
            file.file_name = new_name
            file.save()
            messages.success(request, "File renamed successfully.")
            return redirect('file_explorer')
    else:
        form = FileRenameForm(initial={'new_name': file.file_name})
    return render(request, 'rename_file.html', {'form': form, 'file': file})


@login_required
def delete_file_view(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    file.delete()  # This will remove the file from both the database and storage
    messages.success(request, "File deleted successfully.")
    return HttpResponseRedirect(reverse('file_explorer'))


@login_required
def download_file(request, file_id):
    try:
        user_file = UserFile.objects.get(id=file_id, user=request.user)
    except UserFile.DoesNotExist:
        raise Http404("File not found.")

    file_path = os.path.join(settings.MEDIA_ROOT, user_file.file.name)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=user_file.file_name)
    else:
        raise Http404("File not found.")


@login_required
def file_explorer_view(request, folder_id=None):
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, user=request.user)

    # Handle file upload
    if request.method == 'POST' and 'upload_file' in request.POST:
        form = FileUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = request.user
            file_instance.folder = current_folder
            file_instance.file_name = file_instance.file.name
            file_instance.file_size = file_instance.file.size

            # Calculate current storage usage
            current_storage = calculate_user_storage_usage(request.user)
            new_total_storage = current_storage + file_instance.file_size

            # Enforce 100 MB limit (100 * 1024 * 1024 bytes)
            if new_total_storage <= 100 * 1024 * 1024:
                file_instance.save()
                messages.success(request, "File uploaded successfully.")
            else:
                messages.error(request, "Upload failed. You have exceeded your 100 MB storage limit.")

            # Correct redirect logic based on folder presence
            if current_folder:
                return redirect('file_explorer', folder_id=current_folder.id)
            else:
                return redirect('file_explorer')
        else:
            # Display form validation errors, including file size errors
            for error in form.errors.values():
                messages.error(request, error)
    # Calculate storage usage and retrieve files and subfolders
    form = FileUploadForm(user=request.user)
    subfolders = Folder.objects.filter(user=request.user, parent_folder=current_folder)
    user_files = UserFile.objects.filter(user=request.user, folder=current_folder)
    current_storage = calculate_user_storage_usage(request.user)

    return render(request, 'file_explorer.html', {
        'form': form,
        'subfolders': subfolders,
        'user_files': user_files,
        'current_folder': current_folder,
        'current_storage': current_storage,
    })




@login_required
def create_folder_view(request, parent_folder_id=None):
    parent_folder = None
    if parent_folder_id:
        parent_folder = get_object_or_404(Folder, id=parent_folder_id, user=request.user)

    if request.method == 'POST':
        folder_form = FolderCreateForm(request.POST)
        if folder_form.is_valid():
            new_folder = folder_form.save(commit=False)
            new_folder.user = request.user
            new_folder.parent_folder = parent_folder
            new_folder.save()
            messages.success(request, "Folder created successfully.")
            if parent_folder:
                return redirect('file_explorer', folder_id=parent_folder.id)
            else:
                return redirect('file_explorer')
    else:
        folder_form = FolderCreateForm()

    return render(request, 'create_folder.html', {
        'folder_form': folder_form,
        'parent_folder': parent_folder,
    })


@login_required
def rename_folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == 'POST':
        form = FolderCreateForm(request.POST, instance=folder)
        if form.is_valid():
            form.save()
            parent_folder_id = folder.parent_folder.id if folder.parent_folder else None
            messages.success(request, "Folder renamed successfully.")
            return redirect('file_explorer', folder_id=parent_folder_id) if parent_folder_id else redirect('file_explorer')
    else:
        form = FolderCreateForm(instance=folder)
    return render(request, 'rename_folder.html', {'form': form, 'folder': folder})


@login_required
def delete_folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    parent_folder_id = folder.parent_folder.id if folder.parent_folder else None
    folder.delete()
    messages.success(request, "Folder deleted successfully.")
    return redirect('file_explorer', folder_id=parent_folder_id) if parent_folder_id else redirect('file_explorer')


@login_required
def move_file_view(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    if request.method == 'POST':
        form = MoveFileForm(request.POST, user=request.user)
        if form.is_valid():
            target_folder = form.cleaned_data['target_folder']
            file.folder = target_folder
            file.save()
            messages.success(request, "File moved successfully.")
            return redirect('file_explorer', folder_id=target_folder.id if target_folder else None)
    else:
        form = MoveFileForm(user=request.user)

    return render(request, 'move_file.html', {'form': form, 'file': file})


@login_required
def copy_file_view(request, file_id):
    file = get_object_or_404(UserFile, id=file_id, user=request.user)
    if request.method == 'POST':
        form = CopyFileForm(request.POST, user=request.user)
        if form.is_valid():
            target_folder = form.cleaned_data['target_folder']
            copied_file = UserFile.objects.create(
                user=request.user,
                folder=target_folder,
                file=file.file,
                file_name=f"Copy of {file.file_name}",
                file_size=file.file_size,
            )
            messages.success(request, "File copied successfully.")
            return redirect('file_explorer', folder_id=target_folder.id if target_folder else None)
    else:
        form = CopyFileForm(user=request.user)

    return render(request, 'copy_file.html', {'form': form, 'file': file})


def calculate_user_storage_usage(user):
    storage_usage = UserFile.objects.filter(user=user).aggregate(total_size=Sum('file_size'))
    return storage_usage['total_size'] or 0