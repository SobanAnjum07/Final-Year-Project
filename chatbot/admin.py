from django.contrib import admin

# Register your models here.
# chatbot/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ChatMessage

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']

# Register the CustomUser model
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ChatMessage)
