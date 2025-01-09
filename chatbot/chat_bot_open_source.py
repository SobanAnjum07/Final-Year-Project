import os
import gdown
import PyPDF2
import tensorflow as tf

tf.get_logger().setLevel("ERROR")
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings


import os
import PyPDF2
from PyPDF2.errors import PdfReadError


def extract_text_from_pdfs(pdf_dir):
    texts = []
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith(".pdf"):
            try:
                pdf_path = os.path.join(pdf_dir, pdf_file)
                with open(pdf_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    # Check if the PDF is encrypted
                    if reader.is_encrypted:
                        try:
                            reader.decrypt(
                                ""
                            )  # Attempt to decrypt with an empty password
                        except PdfReadError:
                            print(f"Skipping encrypted PDF: {pdf_file}")
                            continue

                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    texts.append(text)
            except Exception as e:
                print(f"Error reading {pdf_file}: {e}")
    return texts


# Call the function and handle the results
texts = extract_text_from_pdfs("pdfs")

if not texts:
    raise ValueError("No text extracted from PDFs. Please check the input directory.")


# Step 3: Split Text into Smaller Chunks
def split_text_into_chunks(texts):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )  # Smaller chunks
    documents = [
        Document(page_content=text) for text in texts
    ]  # Wrap texts into Document objects
    split_documents = splitter.split_documents(documents)
    return split_documents


documents = split_text_into_chunks(texts)


# Step 4: Create a Vector Store
def create_vector_store(documents):
    # Extract plain text from the Document objects
    texts = [doc.page_content for doc in documents]

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create the FAISS vector store
    vector_store = FAISS.from_texts(texts, embeddings)
    return vector_store


vector_store = create_vector_store(documents)


# Step 5: Build the RAG Pipeline
groq_api_key = "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"


def build_rag_pipeline(vector_store):
    retriever = vector_store.as_retriever()
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        max_tokens=32768,
        temperature=0.7,
    )

    prompt = ChatPromptTemplate.from_template(
        """
        Answer the questions based on the provided context only.
        Provide the most accurate response based on the question.
        <context>
        {context}
        <context>
        Question: {input}
        """
    )

    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, chain_type="stuff"
    )
    return retrieval_chain


qa_chain = build_rag_pipeline(vector_store)


# Query the chatbot
def query_chatbot(qa_chain, query):
    response = qa_chain.invoke({"query": query})
    return response["result"]
# print("What do you want to ask? : ")
query = input("What do you want to ask? : ")
while query != "quit":
    # print("")
    
    response = query_chatbot(qa_chain, query)
    print(response)
    query = input("What do you want to ask? : ")
