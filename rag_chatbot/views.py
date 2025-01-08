from django.shortcuts import render
from django.http import JsonResponse

from chatbot.models import *

import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

import threading

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Function to extract text from a single PDF
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF."""
    try:
        document = fitz.open(pdf_path)
        text = ""
        for page in document:
            text += page.get_text()
        document.close()
        return text
    except Exception as e:
        raise ValueError(f"Error reading {pdf_path}: {e}")

# Function to process and index multiple PDFs
def create_combined_index(pdf_paths, chunk_size=1000, overlap=200):
    """Create a unified FAISS vector index from multiple PDFs."""
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    texts, metadata = [], []

    for pdf_path in pdf_paths:
        try:
            text = extract_text_from_pdf(pdf_path)
            # Chunk text with overlap
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i + chunk_size]
                texts.append(chunk)
                metadata.append({"source": os.path.basename(pdf_path)})
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    # Create FAISS index with metadata
    index = FAISS.from_texts(texts, embeddings, metadatas=metadata)
    return index

# Function to process queries
def ask_question(index, query, chat_history=None):
    """Ask a question using the RAG framework."""
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, temperature=0.7)
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=index.as_retriever(search_type="similarity"),
            verbose=False,
            return_source_documents=True,  # Ensures we can check sources
        )

        response = chain.invoke({"question": query, "chat_history": chat_history or []})
        answer = response["answer"]
        source_documents = response["source_documents"]

        # Check if the answer is supported by the source documents
        if not source_documents:
            return "I'm sorry, I couldn't find an answer in the provided documents."
        
        return answer
    except Exception as e:
        return f"Error during query processing: {e}"

# Markdown formatting
def format_markdown(answer, source=None):
    """Format the answer in Markdown."""
    markdown = f"**Chatbot Response:**\n\n```markdown\n{answer}\n```"
    if source:
        markdown += f"\n\n**Source:** {source}"
    return markdown



def chatbot_logic():
    # Define the directories
    app_pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    external_pdf_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "faculty")

    lectures_dir = os.path.join(external_pdf_dir, "lectures")
    resumes_dir = os.path.join(external_pdf_dir, "resumes")

    # Check if the directories exist
    for directory in [lectures_dir, resumes_dir, external_pdf_dir]:
        if not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")

    # Gather all PDF paths from 'lectures', 'resumes', and 'faculty'
    pdf_paths = [
        os.path.join(app_pdf_dir, f) for f in os.listdir(app_pdf_dir) if f.endswith(".pdf")
    ] + [os.path.join(lectures_dir, f) for f in os.listdir(lectures_dir) if f.endswith(".pdf")
    ] + [
        os.path.join(resumes_dir, f) for f in os.listdir(resumes_dir) if f.endswith(".pdf")
    ]

    if not pdf_paths:
        raise ValueError("No PDFs found in the directories.")

    print("Extracting text and creating combined index...")
    index = create_combined_index(pdf_paths)

    return index

index = chatbot_logic()

# def chatbot(request):
#     if request.method == 'POST':
#         message = request.POST.get('message')
        
#         # Process query using the chatbot logic
#         response = ask_question(index, message)
        
#         # Return the response as JSON
#         return JsonResponse({'message': message, 'response': response})

#     return render(request, 'chatbot.html')


def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        
        # Save user's message to the database
        ChatMessage.objects.create(user=request.user, message=user_input, is_bot=False)

        # Get the chatbot's response
        bot_response = ask_question(index, user_input)
        
        # Save bot's response to the database
        ChatMessage.objects.create(user=request.user, message=bot_response, is_bot=True)

    # Fetch all messages for the logged-in user
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')

    return render(request, 'chatbot.html', {'messages': messages})