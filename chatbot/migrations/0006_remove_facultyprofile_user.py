# Generated by Django 5.1.3 on 2024-12-30 20:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0005_facultyprofile_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facultyprofile',
            name='user',
        ),
    ]
