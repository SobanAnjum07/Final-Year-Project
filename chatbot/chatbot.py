import os
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Ensure nltk tokenizer is downloaded
nltk.download("punkt")
nltk.download('punkt_tab')


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF."""
    try:
        document = fitz.open(pdf_path)
        text = "\n".join([page.get_text() for page in document])
        document.close()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading {pdf_path}: {e}")


def chunk_text(text, chunk_size=1000, overlap=200):
    """Smart chunking of text while preserving sentence boundaries."""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        if sum(len(s) for s in current_chunk) + len(sentence) <= chunk_size:
            current_chunk.append(sentence)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]  # Start a new chunk

    if current_chunk:  # Append last chunk
        chunks.append(" ".join(current_chunk))

    return chunks


def create_combined_index(pdf_paths, chunk_size=1000, overlap=200):
    """Create a unified FAISS vector index from multiple PDFs."""
    if not openai_api_key:
        raise ValueError("Error: Missing OpenAI API key.")

    embeddings = OpenAIEmbeddings()  # No need for api_key argument
    texts, metadata = [], []

    for pdf_path in pdf_paths:
        try:
            text = extract_text_from_pdf(pdf_path)
            if not text.strip():
                print(f"Warning: No text extracted from {pdf_path}. Skipping...")
                continue

            chunks = chunk_text(text, chunk_size, overlap)
            for chunk in chunks:
                texts.append(chunk)
                metadata.append({"source": os.path.basename(pdf_path)})

        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    # Debugging output
    print(f"✅ Total chunks created: {len(texts)}")

    if not texts:
        raise ValueError("Error: No text chunks created. Check PDF extraction.")

    return FAISS.from_texts(texts, embeddings, metadatas=metadata)


def ask_question(index, query, chat_history=None):
    """Ask a question using the RAG framework."""
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=index.as_retriever(search_type="similarity"),
            verbose=False,
            return_source_documents=True,
        )

        response = chain.invoke({"question": query, "chat_history": chat_history or []})
        answer = response.get("answer", "I'm sorry, I couldn't find an answer.")
        source_docs = response.get("source_documents", [])

        if not source_docs:
            return "I'm sorry, I couldn't find an answer in the provided documents."

        return answer
    except Exception as e:
        return f"Error during query processing: {e}"


def main():
    """Main chatbot execution."""
    pdf_dir = "./pdfs"  # Update to match your PDF directory
    if not os.path.isdir(pdf_dir):
        print("Error: PDF directory not found.")
        return

    pdf_paths = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    print(pdf_paths)
    if not pdf_paths:
        print("Error: No PDFs found in the directory.")
        return

    print("Extracting text and creating FAISS index...")
    try:
        index = create_combined_index(pdf_paths)
    except ValueError as e:
        print(e)
        return

    print("\n✅ Chatbot is ready! Type your questions below.")
    chat_history = []

    while True:
        user_input = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        print("🔄 Processing your question...")
        answer = ask_question(index, user_input, chat_history)
        chat_history.append((user_input, answer))
        print(f"\n🗨️ {answer}")


if __name__ == "__main__":
    main()