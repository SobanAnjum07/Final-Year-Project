from django.test import TestCase
import os
from .sobanrag import PDFChatbot
# Create your tests here.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory containing the script
PDF_DIR = os.path.join(BASE_DIR, "pdfs")  # PDFs located in the "pdfs" folder

# Initialize the chatbot with the local PDFs
chatbot_instance = PDFChatbot(pdf_dir=PDF_DIR)

# Example query to test the chatbot
query = "What is the main topic of the document?"

# Ask the chatbot
try:
    response = chatbot_instance.ask(query)
    print(f"Chatbot Response: {response}")
except Exception as e:
    print(f"Error querying the chatbot: {e}")