import os
import fitz  # PyMuPDF
import pickle
import nltk
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from anthropic import Anthropic
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Ensure nltk tokenizer is downloaded
nltk.download('punkt')
nltk.download('punkt_tab')  # Add this line to download the required resource

# FAISS Index Storage Paths
INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiss_index")
INDEX_FILE = os.path.join(INDEX_DIR, "faiss_index")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.pkl")

# Load OpenAI embeddings
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

def save_faiss_index(index, metadata):
    """Save FAISS index and metadata."""
    os.makedirs(INDEX_DIR, exist_ok=True)
    index.save_local(INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)
    print("✅ FAISS index updated and saved!")

def load_faiss_index():
    """Load FAISS index and metadata if they exist."""
    if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
        print("✅ Loading existing FAISS index...")
        index = FAISS.load_local(INDEX_FILE, embeddings, allow_dangerous_deserialization=True)
        with open(METADATA_FILE, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata
    return None, {}

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF."""
    document = fitz.open(pdf_path)
    text = " ".join([page.get_text() for page in document])
    print(f"📄 Extracted text from {pdf_path}: {text[:100]}...")
    document.close()
    return text.strip()

def chunk_text(text, chunk_size=1000, overlap=850):
    """Smart chunking of text while preserving sentence boundaries."""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        if sum(len(s) for s in current_chunk) + len(sentence) <= chunk_size:
            current_chunk.append(sentence)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks



def create_or_update_faiss_index(pdf_paths, chunk_size=850, overlap=800):
    """Create or update the FAISS index with given PDFs."""
    index, metadata = load_faiss_index()

    if not pdf_paths:
        print("⚠️ No PDF paths provided!")
        return None

    existing_pdfs = set(metadata.keys())
    new_pdfs = set(os.path.basename(f) for f in pdf_paths) - existing_pdfs

    texts, metadatas = [], []

    for pdf_path in pdf_paths:
        pdf_name = os.path.basename(pdf_path)
        if pdf_name not in new_pdfs:
            continue  # Already processed

        print(f"🔄 Processing new PDF: {pdf_name}")
        try:
            text = extract_text_from_pdf(pdf_path)
            chunks = chunk_text(text, chunk_size, overlap)
            texts.extend(chunks)
            metadatas.extend([{"source": pdf_name}] * len(chunks))
            metadata[pdf_name] = len(chunks)
        except Exception as e:
            print(f"❌ Error processing {pdf_name}: {e}")

    if texts:
        if index:
            print(f"📌 Adding {len(texts)} new chunks to existing FAISS index...")
            index.add_texts(texts, metadatas=metadatas)
        else:
            print(f"🆕 Creating FAISS index with {len(texts)} chunks...")
            index = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

        save_faiss_index(index, metadata)
    else:
        print("⚠️ No new text chunks created. Check PDF content.")

    return index

# Load Claude API key
claude_api_key = os.getenv("CLAUDE_API_KEY")
anthropic_client = Anthropic(api_key=claude_api_key)

def ask_question_with_openai(index, query, chat_history=None):
    """Ask a question using GPT-3.5 with enhanced prompt and retrieval depth."""
    if chat_history is None:
        chat_history = []

    try:
        # Custom prompt template for better reasoning
        prompt_template = """You are an expert assistant for FYP-related technical topics.
                Please ensure that your answers are based on the context provided and are accurate and relevant.
                When answering the user's question, first explain the concept if needed, and then provide related commands or steps using ONLY the context below.
                If the answer is not explicitly in the context, say "I don't know."
                Try to find the answer in the uploaded documents.
                Context:
                {context}

                Question: {question}
                Answer:"""

        PROMPT = PromptTemplate(
            input_variables=["context", "question"],
            template=prompt_template,
        )

        # Use more chunks (increase k)
        # Increase retrieval depth for more comprehensive context
        retriever = index.as_retriever(
            search_type="similarity", 
            search_kwargs={
                "k": 12,  # Retrieve more chunks
                "fetch_k": 20,  # Consider more candidates
                "score_threshold": 0.5  # Only include relevant chunks
            }
        )
        
        llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, temperature=0.5)

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=True,
            # Add chain type configuration
            chain_type="stuff",  # Use 'map_reduce' for very large contexts
            # Add memory configuration
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                output_key="answer",
                return_messages=True
            )
        )

        response = chain.invoke({"question": query, "chat_history": chat_history})
        answer = response["answer"]
        source_documents = response["source_documents"]

        if not source_documents:
            chat_history.append((query, "I'm sorry, I couldn't find an answer in the provided documents."))
            return "I'm sorry, I couldn't find an answer in the provided documents.", chat_history

        chat_history.append((query, answer))
        return answer, chat_history

    except Exception as e:
        error_msg = f"Error during query processing: {e}"
        chat_history.append((query, error_msg))
        return error_msg, chat_history

def ask_question_with_claude(index, query, chat_history=None):
    """Ask a question using FAISS + Claude for deep reasoning, using Anthropic-style chat format."""
    if chat_history is None:
        chat_history = []

    try:
        # Retrieve relevant documents from FAISS
        retriever = index.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        docs = retriever.get_relevant_documents(query)
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)

        if not context:
            response = "I'm sorry, I couldn't find an answer in the provided documents."
            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": response})
            return response, chat_history

        # Add context as part of the user message
        user_message = f"""Here is some background information:\n{context}\n\nNow, answer this question:\n{query}"""

        # Build full conversation with context-aware turn history
        messages = chat_history + [{"role": "user", "content": user_message}]

        # Call Claude
        completion = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.8,
            system="You are a highly knowledgeable assistant. Use the provided context to answer questions clearly and accurately.",
            messages=messages
        )

        # Extract response
        answer = completion.content[0].text.strip()

        # Append new interaction to chat history
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": answer})

        return answer, chat_history

    except Exception as e:
        error_msg = f"Error during query processing: {e}"
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": error_msg})
        return error_msg, chat_history


USE_CLAUDE = False

def ask_question(index, query, chat_history=None):
    if USE_CLAUDE:
        return ask_question_with_claude(index, query, chat_history)
    else:
        return ask_question_with_openai(index, query, chat_history)

def format_markdown(answer, source=None):
    """Format the answer in Markdown."""
    markdown = f"**Chatbot Response:**\n\n```markdown\n{answer}\n```"
    if source:
        markdown += f"\n\n**Source:** {source}"
    return markdown

def main():
    pdf_dir = "./pdfs"  # Directory containing PDFs

    if not os.path.isdir(pdf_dir):
        print("Error: Directory not found.")
        return

    pdf_paths = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    if not pdf_paths:
        print("Error: No PDFs found in the directory.")
        return

    print("📌 Checking and updating FAISS index...")
    index = create_or_update_faiss_index(pdf_dir)

    print("\n🤖 Chatbot is ready! Type your questions below.")
    chat_history = []

    while True:
        user_input = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        print("💬 Processing your question...")
        answer = ask_question(index, user_input, chat_history)
        chat_history.append((user_input, answer))
        print(answer)
