import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
import os

VAULT_PATH = "./test_data/Obsidian Main Copy"
# VAULT_PATH = "./test_data/obsidian"
base_dir_abs = os.path.abspath(VAULT_PATH)

class Chatbot:
    def __init__(self, load_documents=True):
        """Initialize the chatbot with RAG (Retrieval-Augmented Generation)."""
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.chroma_collection = self.chroma_client.get_or_create_collection("tech16example")
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Create Vector index with or without loading documents
        if load_documents and vault_path:
            print("loading documents")
            documents = SimpleDirectoryReader(
                VAULT_PATH, required_exts=[".md"], recursive=True
            ).load_data()
            self.index = VectorStoreIndex.from_documents(documents, storage_context=self.storage_context)
            print('done')
        else:
            print("opening vector store")
            self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)

        # Set up LLM
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.7)
        self.query_engine = self.index.as_query_engine(similarity_top_k=10)

    def ask_with_context(self, query: str, context: str):
        """Get answer from LLM given the provided context."""

        # Generate response using LLM with retrieved context
        prompt = f"Using the following context, answer the query: '{query}'\n\n{context}"
        response = Settings.llm.complete(prompt)

        return response

    def ask_with_rag(self, query: str) -> str:
        """Process the query using RAG and return the chatbot's response."""
        retrieved_docs = self.query_engine.retrieve(query)
        
        if not retrieved_docs:
            return "I couldn't find relevant information for your query."

        # Extract text content from selected documents
        context_text = "\n\n".join(doc.text for doc in retrieved_docs)

        # Generate response using LLM with retrieved context
        prompt = f"Using the following documents, answer the query: '{query}'\n\n{context_text}"
        response = Settings.llm.complete(prompt)

        return response

    def find_rag_document(self, query: str) -> str:
        """Process the query using RAG and return the chatbot's response."""
        retrieved_docs = self.query_engine.retrieve(query)
        print(len(retrieved_docs))
        # print(retrieved_docs)
        
        paths = []
        for doc in retrieved_docs:
            # print(base_dir_abs, doc.metadata.get('file_path'))
            paths.append(os.path.relpath(doc.metadata.get('file_path'), base_dir_abs))

        print(paths)

        return paths



# Create a chatbot instance for Flask to use
# chatbot = Chatbot(load_documents=True)
