import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

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
        llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key, temperature=0.7)
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

# Main chatbot logic
def main():
    # Get a list of PDFs
    pdf_dir = "./pdfs"  # Update to match your PDF directory
    if not os.path.isdir(pdf_dir):
        print("Error: Directory not found.")
        return

    pdf_paths = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    if not pdf_paths:
        print("Error: No PDFs found in the directory.")
        return

    # print("Extracting text and creating combined index...")
    index = create_combined_index(pdf_paths)

    # print("\nChatbot is ready! Type your questions below.")
    chat_history = []

    while True:
        user_input = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # print("Processing your question...")
        answer = ask_question(index, user_input, chat_history)
        chat_history.append((user_input, answer))
        print(answer)

if __name__ == "__main__":
    main()