# chatbot/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, FacultyProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    full_name = forms.CharField(required=True, label='Full Name', widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))  # ✅ Add this

    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'role-select'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'email', 'password1', 'password2', 'role']  # ✅ Add full_name here



class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['name', 'contact', 'email', 'resume', 'lecture_slides']
