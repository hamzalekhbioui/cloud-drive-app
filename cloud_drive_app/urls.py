from django.urls import path
from django.urls import path
from . import views  # This should be included to import views
from .views import (
    login_view, register_view, file_explorer_view, create_folder_view,
    rename_file_view, delete_file_view, download_file, account_info_view,
    rename_folder_view, delete_folder_view, move_file_view, copy_file_view
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('file_explorer/', views.file_explorer_view, name='file_explorer'),
    path('delete/<int:file_id>/', delete_file_view, name='delete_file'),
    path('rename/<int:file_id>/', rename_file_view, name='rename_file'),
    path('account_info/', account_info_view, name='account_info'),

    #path('statistics/', file_statistics_view, name='file_statistics'),
    path('<int:folder_id>/', file_explorer_view, name='file_explorer'),
    #path('', file_explorer_view, name='file_explorer'),  # Root folder
    path('create_folder/', create_folder_view, name='create_folder'),
    path('create_folder/<int:parent_folder_id>/', create_folder_view, name='create_subfolder'),
    path('rename_folder/<int:folder_id>/', rename_folder_view, name='rename_folder'),
    path('delete_folder/<int:folder_id>/', delete_folder_view, name='delete_folder'),
    path('move_file/<int:file_id>/', move_file_view, name='move_file'),
    path('copy_file/<int:file_id>/', copy_file_view, name='copy_file'),
    path('download/<int:file_id>/', download_file, name='download_file'),
]




