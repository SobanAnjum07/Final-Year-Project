from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.template import loader

from .models import FacultyProfile

from .forms import FacultyProfileForm, CustomUserCreationForm

# Create your views here.
# chatbot/views.py

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print('hello')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            print('logged in')
            messages.success(request, "Logged in successfully!")
            # Redirect to the home page
            return redirect('home')
        else:
            # Invalid credentials
            print('not correct')
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'chatbot/login-page.html')
# chatbot/views.py


def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('login')  # Redirect to the login page



def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Replace 'login' with the name of your login URL
    else:
        form = CustomUserCreationForm()
    return render(request, 'chatbot/signup-page.html', {'form': form})


def home_page(request):
    return render(request,'chatbot/home.html')


from django.shortcuts import render, get_object_or_404, redirect
from .models import FacultyProfile
from .forms import FacultyProfileForm

def create_or_edit_faculty_profile(request, profile_id=None):
    # Get the current user
    user = request.user

    # Check if the user already has a profile or create a new one
    if profile_id:
        faculty_profile = get_object_or_404(FacultyProfile, id=profile_id, user=user)
    else:
        faculty_profile = None

    if request.method == "POST":
        form = FacultyProfileForm(request.POST, request.FILES, instance=faculty_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user  # Set the user field manually
            profile.save()
            return redirect('faculty_profiles_list')  # Redirect to the list of profiles after saving
    else:
        form = FacultyProfileForm(instance=faculty_profile)

    return render(request, 'chatbot/faculty_profile_form.html', {'form': form})

def faculty_profile_view(request, id):
    profile = get_object_or_404(FacultyProfile, id=id)

    if request.method == 'POST':
        form = FacultyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile data to the database
            return redirect('faculty_profiles_list')  # Redirect to the list of profiles after saving
    else:
        form = FacultyProfileForm(instance=profile)  # Populate the form with the existing data

    return render(request, 'chatbot/faculty_profile_view.html', {'form': form, 'profile': profile})

def list_faculty_profiles(request):
    # Fetch all the faculty profiles
    faculty_profiles = FacultyProfile.objects.all()

    # Pass the faculty profiles to the template
    return render(request, 'chatbot/faculty_profiles_list.html', {'faculty_profiles': faculty_profiles})
