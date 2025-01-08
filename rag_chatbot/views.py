from django.shortcuts import render

from chatbot.models import *

import os
from dotenv import load_dotenv

from rag_chatbot.chatbot_logic import *

import threading
import pyttsx3

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


index = chatbot_logic()

# def chatbot(request):
#     if request.method == 'POST':
#         message = request.POST.get('message')
        
#         # Process query using the chatbot logic
#         response = ask_question(index, message)
        
#         # Return the response as JSON
#         return JsonResponse({'message': message, 'response': response})

#     return render(request, 'chatbot.html')


def text_to_speech(text):
    """Convert text to speech."""
    def speak():
        tts_engine = pyttsx3.init()
        tts_engine.setProperty("rate", 150)
        tts_engine.setProperty("volume", 0.9)
        voices = tts_engine.getProperty("voices")
        tts_engine.setProperty("voice", voices[0].id)
        tts_engine.say(text)
        tts_engine.runAndWait()
    
    # Run text-to-speech in a separate thread so it doesn't block the response rendering
    threading.Thread(target=speak).start()


def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        
        # Save user's message to the database
        ChatMessage.objects.create(user=request.user, message=user_input, is_bot=False)

        # Get the chatbot's response
        bot_response = ask_question(index, user_input)

        text_to_speech(bot_response)
        
        # Save bot's response to the database
        ChatMessage.objects.create(user=request.user, message=bot_response, is_bot=True)

    # Fetch all messages for the logged-in user
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')

    return render(request, 'chatbot.html', {'messages': messages})