from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core.storage import StorageContext
from dotenv import load_dotenv
import os
import re
from datetime import datetime
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

script_dir = os.path.dirname(os.path.abspath(__file__))
chroma_db_path = os.path.join(script_dir, "../chroma_db")

VAULT_PATH = os.path.join(script_dir, "../test_data/obsidian")
COLLECTION_NAME = "obsidian"
# VAULT_PATH = os.path.join(script_dir, "../test_data/Obsidian Main Copy")
# COLLECTION_NAME = "Obsidian Main Copy"

def load_documents_with_date_metadata(vault_path):
    """
    Custom document loader that extracts date information from filenames
    and enhances document content with that information.
    """
    print("Loading documents with date metadata enhancement...")
    # Load documents using SimpleDirectoryReader
    documents = SimpleDirectoryReader(
        vault_path, required_exts=[".md"], recursive=True
    ).load_data()
    
    # Process documents to add date metadata
    enhanced_documents = []
    date_enhanced_count = 0
    
    for doc in documents:
        # Get file path and check if it's a daily note
        file_path = doc.metadata.get('file_path', '')
        filename = os.path.basename(file_path)
        
        # Extract date from filename if it matches the YYYY-MM-DD pattern
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', filename)
        
        if date_match:
            # Extract date information
            date_str = date_match.group(1)
            try:
                # Parse the date
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                
                # Create new metadata dictionary with date information
                new_metadata = doc.metadata.copy()
                new_metadata['date'] = date_str
                new_metadata['year'] = date_obj.year
                new_metadata['month'] = date_obj.month
                new_metadata['day'] = date_obj.day
                
                # Create a new document with enhanced text (adding date header)
                date_header = f"Date: {date_str}\n"
                new_document = Document(
                    text=date_header + doc.text,
                    metadata=new_metadata
                )
                enhanced_documents.append(new_document)
                date_enhanced_count += 1
            except ValueError:
                # If date parsing fails, add original document
                enhanced_documents.append(doc)
        else:
            # Not a date-named file, add as is
            enhanced_documents.append(doc)
    
    print(f"Enhanced {date_enhanced_count} documents with date metadata out of {len(documents)} total documents")
    return enhanced_documents

def update_vector_store():
    print(f"""Loading documents... 
    from {VAULT_PATH}
    to collection {COLLECTION_NAME}
    """)
    
    # Load documents with date metadata enhancement
    documents = load_documents_with_date_metadata(VAULT_PATH)
    
    # Create or load the storage context
    chroma_client = chromadb.PersistentClient(path=chroma_db_path)
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
