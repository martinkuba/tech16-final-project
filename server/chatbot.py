import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import os
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))

# VAULT_PATH = os.path.join(script_dir, "../test_data/Obsidian Main Copy")
# COLLECTION_NAME = "Obsidian Main Copy"

VAULT_PATH = os.path.join(script_dir, "../test_data/obsidian")
COLLECTION_NAME = "obsidian"
LLM_MODEL = "gpt-4-turbo"
# LLM_MODEL = "gpt-3.5-turbo"

base_dir_abs = os.path.abspath(VAULT_PATH)

class Chatbot:
    def __init__(self):
        """Initialize the chatbot with RAG (Retrieval-Augmented Generation)."""
        # Ensure API key is available
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.chroma_collection = self.chroma_client.get_or_create_collection(COLLECTION_NAME)
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Configure embedding model
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
        
        # Set up LLM
        Settings.llm = OpenAI(model=LLM_MODEL, temperature=0.5)

        # Create Vector index with or without loading documents
        print("opening vector store")
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)

        self.query_engine = self.index.as_query_engine(similarity_top_k=10)
    
    def ask_with_context(self, query: str, context: str):
        """Get answer from LLM given the provided context."""

        # Create a document from your context
        document = Document(text=context)
        
        # Create a simple index
        index = VectorStoreIndex.from_documents([document])
        
        # Query the index (handles chunking and retrieval automatically)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)

        # Extract source nodes if available
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                if 'file_path' in node.node.metadata:
                    sources.append(os.path.relpath(node.node.metadata.get('file_path'), base_dir_abs))
        
        # Return a dictionary with response text and sources
        return {
            "response": str(response.response),
            "sources": sources
        }

    def ask_with_rag(self, query: str):
        """Process the query using RAG and return the chatbot's response and source documents."""
        retrieved_docs = self.query_engine.retrieve(query)
        
        if not retrieved_docs:
            return {
                "response": "I couldn't find relevant information for your query.",
                "sources": []
            }

        # Extract text content from selected documents
        context_text = "\n\n".join(doc.text for doc in retrieved_docs)
        
        # Generate response using LLM with retrieved context
        prompt = f"Using the following documents, answer the query: '{query}'\n\n{context_text}"
        response_obj = Settings.llm.complete(prompt)
        
        # Extract the string content from the CompletionResponse object
        response_text = str(response_obj)
        
        # Extract source document paths
        sources = []
        for doc in retrieved_docs:
            if 'file_path' in doc.metadata:
                sources.append(os.path.relpath(doc.metadata.get('file_path'), base_dir_abs))
        
        return {
            "response": response_text,
            "sources": sources
        }

    def find_rag_document(self, query: str) -> list:
        """
        Process a query and return relevant document paths.
        Uses date filtering if the query contains time expressions.
        """

        retrieved_docs = self.query_engine.retrieve(query)
        
        print(len(retrieved_docs))
        
        paths = []
        for doc in retrieved_docs:
            if hasattr(doc, 'node'):
                # For NodeWithScore objects
                if 'file_path' in doc.node.metadata:
                    paths.append(os.path.relpath(doc.node.metadata.get('file_path'), base_dir_abs))
            else:
                # For other types of nodes
                if 'file_path' in doc.metadata:
                    paths.append(os.path.relpath(doc.metadata.get('file_path'), base_dir_abs))

        return paths
