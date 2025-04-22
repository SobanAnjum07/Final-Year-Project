from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout


from .forms import  CustomUserCreationForm

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


from django.shortcuts import render, redirect, get_object_or_404
from .models import FacultyProfile
from .forms import FacultyProfileForm
from django.contrib.auth.decorators import login_required

@login_required
def create_faculty_profile(request):
    # If the user already has a profile, redirect to the dashboard
    if hasattr(request.user, 'facultyprofile'):
        return redirect('faculty_dashboard')

    if request.method == "POST":
        form = FacultyProfileForm(request.POST, request.FILES)
        if form.is_valid():
            faculty_profile = form.save(commit=False)
            faculty_profile.user = request.user
            faculty_profile.save()
            return redirect('faculty_dashboard')
    else:
        form = FacultyProfileForm()
        
    return render(request, "faculty_profiles/create_faculty_profile.html", {"form": form})