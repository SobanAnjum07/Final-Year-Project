import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

class PDFChatbot:
    def __init__(self, pdf_dir, chunk_size=1000, overlap=200):
        """
        Initialize the chatbot with a directory of PDFs.
        Creates a FAISS index and sets up the conversational chain.
        """
        # Load environment variables
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables.")

        self.pdf_dir = pdf_dir
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.index = None
        self.chain = None
        self.chat_history = []

        # Create the index
        self._create_index()
        self._setup_chain()

    def _extract_text_from_pdf(self, pdf_path):
        """Extract text from a single PDF using PyMuPDF."""
        try:
            document = fitz.open(pdf_path)
            text = ""
            for page in document:
                text += page.get_text()
            document.close()
            return text
        except Exception as e:
            raise ValueError(f"Error reading {pdf_path}: {e}")

    def _create_index(self):
        """Create a FAISS index from the PDFs."""
        embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        texts, metadata = [], []

        # Process each PDF
        if not os.path.isdir(self.pdf_dir):
            raise ValueError(f"PDF directory '{self.pdf_dir}' not found.")
        pdf_paths = [os.path.join(self.pdf_dir, f) for f in os.listdir(self.pdf_dir) if f.endswith(".pdf")]
        if not pdf_paths:
            raise ValueError("No PDFs found in the directory.")

        for pdf_path in pdf_paths:
            try:
                text = self._extract_text_from_pdf(pdf_path)
                # Chunk text with overlap
                for i in range(0, len(text), self.chunk_size - self.overlap):
                    chunk = text[i:i + self.chunk_size]
                    texts.append(chunk)
                    metadata.append({"source": os.path.basename(pdf_path)})
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")

        # Create FAISS index with metadata
        self.index = FAISS.from_texts(texts, embeddings, metadatas=metadata)

    def _setup_chain(self):
        """Set up the ConversationalRetrievalChain."""
        llm = ChatOpenAI(model="gpt-4o", api_key=self.openai_api_key, temperature=0.7)
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.index.as_retriever(search_type="similarity"),
            verbose=False,
            return_source_documents=True,
        )

    def ask(self, query):
        """
        Process a user query using the RAG framework.
        Returns the answer and appends to chat history.
        """
        if not self.chain:
            raise ValueError("Chain is not initialized.")
        try:
            response = self.chain.invoke({"question": query, "chat_history": self.chat_history})
            answer = response["answer"]
            self.chat_history.append((query, answer))
            return answer
        except Exception as e:
            return f"Error during query processing: {e}"
        

# Hardcoded PDF directory path
# pdf_directory = "/home/nauman/DataVerse/chatbot/pdfs"  # Update with the correct path

# # Create an instance of PDFChatbot
# chatbot = PDFChatbot(pdf_dir=pdf_directory)

# # Example questions to ask the chatbot
# questions = [
#     "What is the main topic of the document?",
# ]

# # Ask each question and print the answer
# for query in questions:
#     print(f"Question: {query}")
#     answer = chatbot.ask(query)
#     print(f"Answer: {answer}\n")


