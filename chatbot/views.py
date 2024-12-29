from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout


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
