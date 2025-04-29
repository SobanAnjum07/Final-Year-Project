from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('clear-history/', views.clear_chat_history, name='clear_chat_history'),
]