from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from dotenv import load_dotenv
import os
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

VAULT_PATH = "test_data/obsidian"
COLLECTION_NAME = "obsidian"
# VAULT_PATH = "test_data/Obsidian Main Copy"
# COLLECTION_NAME = "Obsidian Main Copy"

def update_vector_store():
    print("Loading documents...")
    # Load all markdown documents from the vault
    documents = SimpleDirectoryReader(
        VAULT_PATH, 
        required_exts=[".md"], 
        recursive=True
    ).load_data()
    
    # Create or load the storage context
    # You might want to specify your persist_dir here if you're storing embeddings on disk
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create/update the index with the documents
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context
    )
    
    print("Vector store index has been updated successfully!")
    return index

if __name__ == "__main__":
    update_vector_store() 
