from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)

# ChatMessage model
class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to CustomUser
    message = models.TextField()
    is_bot = models.BooleanField(default=False)  # True if the bot sent the message, else user
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.username} at {self.timestamp}"
