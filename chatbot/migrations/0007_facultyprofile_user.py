# Generated by Django 5.1.3 on 2024-12-30 20:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0006_remove_facultyprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='facultyprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='facultyprofile', to=settings.AUTH_USER_MODEL),
        ),
    ]