from django.shortcuts import render
from django.http import JsonResponse

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from langchain.chat_models import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

import pyttsx3

import threading

import os
from dotenv import load_dotenv

# Create your views here.

def chatbot_logic():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    pdf_files = [
        os.path.join(data_dir, "Handout 1.1 (Lab Environment Setup).pdf"),
        os.path.join(data_dir, "Handout 1.1 (Lab Environment Setup).pdf"),
        os.path.join(data_dir, "Handout 1.2 (Recap of OS with Linux) (1).pdf"),
        os.path.join(data_dir, "Handout 1.3 (Recap of InterNetworking Concepts with Linux) (1).pdf"),
        os.path.join(data_dir, "Handout 2.1 (Ethical Hacking Pentesting and Anonymity).pdf"),
        os.path.join(data_dir, "Handout 2.2 (Reconnaissance Info Gathering and OSINT).pdf"),
        os.path.join(data_dir, "Handout 2.3 (Scanning and Vulnerability Analysis - I).pdf"),
        os.path.join(data_dir, "Handout 2.4 (Scanning and Vulnerability Analysis - II).pdf"),
        os.path.join(data_dir, "Handout 2.5 (Exploitation and Gaining Access).pdf"),
        os.path.join(data_dir, "Handout 2.6 (Generating your own Payloads).pdf"),
        os.path.join(data_dir, "Handout 2.7 (Privilege Escalation).pdf")
    ]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  
        chunk_overlap=100
    )
    
    all_documents = []

    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        pages = loader.load()  
        
        combined_text = " ".join(page.page_content for page in pages)
        chunks = text_splitter.split_text(combined_text)
        
        documents = [Document(page_content=chunk, metadata={"source": pdf_file}) for chunk in chunks]
        all_documents.extend(documents)

    combined_docs = " ".join(doc.page_content for doc in all_documents)

    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

    embedding_model = OpenAIEmbeddings()

    db = Chroma.from_documents(documents, embedding_model)

    llm = ChatOpenAI(model = "gpt-3.5-turbo", max_tokens=500, temperature=0.1)
    
    prompt = ChatPromptTemplate.from_template("""
        Answer the following question using only the information provided in the context! 
        Do not add, infer, or assume any details that are not in the context. If the information is not present in the context, simply respond with "Not available in the context."
        But do not add any disclaimers.
        But generate response in more human friendly statements like using paragraph and bullet points for elaboration on types, etc
        End your response with complete sentence.
        <context>
        {context}
        </context>
        Question: {input}""")
    
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever=db.as_retriever(search_type="similarity", k=1)

    return document_chain, retriever

document_chain, retriever = chatbot_logic()
retrieval_chain=create_retrieval_chain(retriever,document_chain)


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

import re

def format_response(response_text):
    """Format the response text by converting bullet points (dashes) to HTML list items."""
    # Split the response into paragraphs (by line break)
    paragraphs = response_text.split("\n")
    
    # Create a list to store the formatted HTML
    formatted_response = []
    is_bullet_point = False

    for para in paragraphs:
        para = para.strip()  # Remove extra spaces before and after the text
        if para.startswith("-"):
            if not is_bullet_point:
                # Start a new unordered list if it's the first bullet point
                formatted_response.append("<ul>")
                is_bullet_point = True
            formatted_response.append(f"<li>{para.strip('-').strip()}</li>")  # Add each bullet point
        else:
            if is_bullet_point:
                # Close the unordered list after the last bullet point
                formatted_response.append("</ul>")
                is_bullet_point = False
            # Add regular paragraphs as <p> tags
            formatted_response.append(f"<p>{para}</p>")

    # If the response ended with bullet points, close the list
    if is_bullet_point:
        formatted_response.append("</ul>")
    
    # Join the formatted response into a single string
    return "".join(formatted_response)


def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        
        # Get response from the retrieval chain
        response = retrieval_chain.invoke({"input": message})
        
        # Format the response into a neat HTML format
        formatted_response = format_response(response['answer'])
        
        # Convert the formatted response to speech
        text_to_speech(response['answer'])

        # Return the formatted response as a JSON response
        return JsonResponse({'message': message, 'response': formatted_response})

    return render(request, 'chatbot.html')