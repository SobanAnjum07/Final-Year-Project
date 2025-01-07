# chatbot/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
