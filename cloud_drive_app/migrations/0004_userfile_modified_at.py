# Generated by Django 4.2.3 on 2024-11-05 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_drive_app', '0003_rename_parent_folder_parent_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='userfile',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]