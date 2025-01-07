from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from .myrag import InstructorChatModel
from .models import ChatMessage
from django.contrib.auth.decorators import login_required
from .sobanrag import PDFChatbot
import os
from django.http import JsonResponse
# # Create your views here.
# # chatbot/views.py

# Define the base directory and PDF directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory containing views.py
PDF_DIR = os.path.join(BASE_DIR, "pdfs")  # PDFs located in the "pdfs" folder

# Initialize the chatbot with the local PDFs
# chatbot_instance = PDFChatbot(pdf_dir=PDF_DIR)
chatbot_instance = InstructorChatModel()

# @login_required
# def chatbot_view(request):
#     """
#     Handles chatbot interactions. Processes user input, gets the chatbot's response,
#     and stores the conversation in the database.
#     """
#     if request.method == 'POST':
#         user_input = request.POST.get('user_input')
        
#         if not user_input:
#             return JsonResponse({"error": "User input is required."}, status=400)

#         # Save user's message to the database
#         ChatMessage.objects.create(user=request.user, message=user_input, is_bot=False)

#         # Get the chatbot's response
#         try:
#             bot_response = chatbot_instance.ask(user_input)
#         except Exception as e:
#             bot_response = f"An error occurred: {e}"

#         # Save bot's response to the database
#         ChatMessage.objects.create(user=request.user, message=bot_response, is_bot=True)

#         # Return bot response as JSON (optional for frontend updates)
#         return JsonResponse({"bot_response": bot_response})

#     # Fetch all messages for the logged-in user
#     messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
#     return render(request, 'chatbot/chat.html', {'messages': messages})
# chat_model = InstructorChatModel()
@login_required
def chatbot_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        
        # Save user's message to the database
        ChatMessage.objects.create(user=request.user, message=user_input, is_bot=False)

        # Get the chatbot's response
        bot_response = chatbot_instance.invoke(user_input)
        
        # Save bot's response to the database
        ChatMessage.objects.create(user=request.user, message=bot_response, is_bot=True)

    # Fetch all messages for the logged-in user
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')

    return render(request, 'chatbot/chat.html', {'messages': messages})

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
