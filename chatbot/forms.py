# chatbot/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, FacultyProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']
    
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'role-select'}))


class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['name', 'contact', 'email', 'resume', 'lecture_slides']
