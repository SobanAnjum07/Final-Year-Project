from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    full_name = models.CharField(max_length=255, blank=True, null=True)  # ✅ Add this line

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('professor', 'Professor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"

class FacultyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='facultyprofile', null=True, blank=True)  # Allow null values
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    resume = models.FileField(upload_to='faculty/resumes/', null=True, blank=True)
    lecture_slides = models.FileField(upload_to='faculty/lectures/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.contact}"

class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to CustomUser
    message = models.TextField()
    is_bot = models.BooleanField(default=False)  # True if the bot sent the message, else user
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.username} at {self.timestamp}"