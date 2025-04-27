from django.shortcuts import render
from django.http import JsonResponse

from chatbot.models import *

import os
import threading
import pyttsx3
from dotenv import load_dotenv

# Import functions from the indexing file
from rag_chatbot.chatbot_indexing import (
    extract_text_from_pdf,
    create_or_update_faiss_index,
    ask_question,
    format_markdown,
    load_faiss_index,
)

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def chatbot_logic():
    # Define the directories with correct paths

    
    app_pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    faculty_dir = os.path.join(app_pdf_dir, "faculty")
    lectures_dir = os.path.join(faculty_dir, "lectures")
    resumes_dir = os.path.join(faculty_dir, "resumes")

    for directory in [app_pdf_dir, faculty_dir, lectures_dir, resumes_dir]:
        if not os.path.isdir(directory):
            print(f"[WARNING] Directory not found: {directory}")
        else:
            print(f"📂 Directory exists: {directory}")
            

    # Check if the directories exist
    for directory in [app_pdf_dir, faculty_dir, lectures_dir, resumes_dir]:
        if not os.path.isdir(directory):
            print(f"[WARNING] Directory not found: {directory}")

    # Gather all PDFs
    pdf_paths = []
    for directory in [lectures_dir, resumes_dir]:
        if os.path.isdir(directory):
            pdf_paths += [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".pdf")]
            print(f"Found PDFs in {directory}: {[f for f in os.listdir(directory) if f.endswith('.pdf')]}")

    if not pdf_paths:
        raise Exception("🚨 No PDFs found to create FAISS index.")

    # Load existing index if any
    index, _ = load_faiss_index()

    if index is None:
        print("[INFO] No existing FAISS index found. Building new one...")
        index = create_or_update_faiss_index(pdf_paths)

    if index is None:
        raise Exception("🚨 Failed to create FAISS index!")

    print("[SUCCESS] FAISS index is ready ✅")
    return index