from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from chatbot.models import ChatMessage
import os
import json
from dotenv import load_dotenv
from rag_chatbot.chatbot_logic import chatbot_logic, ask_question, main
import threading
import pyttsx3

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

print("[STARTUP] Creating or loading FAISS index...")

index = chatbot_logic()

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
    
    threading.Thread(target=speak).start()

@login_required
def chatbot(request):
    global index
    
    # Get or initialize chat history from session
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    
    # Convert the chat history to the correct format
    chat_history = [tuple(pair) for pair in request.session['chat_history']]

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '').strip()

            if not user_input:
                return JsonResponse({'error': 'Empty message'}, status=400)

            # Save user's message
            ChatMessage.objects.create(user=request.user, message=user_input, is_bot=False)

            # Get bot response with chat history
            bot_response, updated_history = ask_question(index, user_input, chat_history)
            
            # Convert updated history to a format that can be stored in session
            request.session['chat_history'] = [[q, a] for q, a in updated_history]
            request.session.modified = True

            # Save bot's response
            ChatMessage.objects.create(user=request.user, message=bot_response, is_bot=True)

            # text_to_speech(bot_response)

            return JsonResponse({'bot_response': bot_response})

        except Exception as e:
            print(f"Error processing chatbot request: {e}")
            return JsonResponse({'error': 'Something went wrong.'}, status=500)

    else:
        # GET method
        messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        return render(request, 'chatbot.html', {'messages': messages})

@login_required
def clear_chat_history(request):
    """Clear the chat history from session and database."""
    if request.method == 'POST':
        # Clear session history
        request.session['chat_history'] = []
        request.session.modified = True
        
        # Clear database messages
        ChatMessage.objects.filter(user=request.user).delete()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
