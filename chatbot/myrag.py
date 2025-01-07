import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

class InstructorChatModel:
    def __init__(self):
        # Load API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = "dr-arif-butt"

        # Initialize components
        self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        self.pinecone_store = PineconeVectorStore(index_name=self.index_name, embedding=self.embeddings)

        # Define the prompt template
        template = """
        Answer the question based on the context below. If you can't 
        answer the question, reply "I don't know".

        Context: {context}

        Question: {question}
        """
        self.prompt = ChatPromptTemplate.from_template(template)

        # Initialize the model
        self.model = ChatOpenAI(openai_api_key=self.openai_api_key, model="gpt-3.5-turbo")
        self.retriever = self.pinecone_store.as_retriever()
        self.parser = StrOutputParser()

        # Build the chain
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | self.parser
        )

    def invoke(self, question):
        try:
            # Call the chain with the question
            return self.chain.invoke(question)
        except Exception as e:
            return f"Error: {str(e)}"

