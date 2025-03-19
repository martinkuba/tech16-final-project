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

# VAULT_PATH = "./test_data/Obsidian Main Copy"
# COLLECTION_NAME = "Obsidian Main Copy"

VAULT_PATH = "./test_data/obsidian"
COLLECTION_NAME = "obsidian"

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
        # Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.7)
        Settings.llm = OpenAI(model="gpt-4-turbo", temperature=0.7)

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

        print(vars(response))
        
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

    def preprocess_time_query(self, query):
        """
        Identify time expressions in queries and return information about the time period.
        This helps with filtering documents by date in the retrieval process.
        """
        # Current date information for relative time references
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Initialize time filter metadata
        time_filter = None
        
        # Check for time-related terms
        if any(term in query.lower() for term in ["this month", "current month"]):
            time_filter = {
                "filter_type": "month",
                "month": current_month,
                "year": current_year,
                "original_query": query,
                "description": f"month {current_month} of {current_year}"
            }
        elif "last month" in query.lower():
            last_month = 12 if current_month == 1 else current_month - 1
            last_month_year = current_year - 1 if current_month == 1 else current_year
            time_filter = {
                "filter_type": "month",
                "month": last_month,
                "year": last_month_year,
                "original_query": query,
                "description": f"month {last_month} of {last_month_year}"
            }
        elif "this year" in query.lower():
            time_filter = {
                "filter_type": "year",
                "year": current_year,
                "original_query": query,
                "description": f"year {current_year}"
            }
        elif any(month_name.lower() in query.lower() for month_name in [
            "january", "february", "march", "april", "may", "june", 
            "july", "august", "september", "october", "november", "december"
        ]):
            # Map month names to numbers
            month_map = {
                "january": 1, "february": 2, "march": 3, "april": 4, 
                "may": 5, "june": 6, "july": 7, "august": 8, 
                "september": 9, "october": 10, "november": 11, "december": 12
            }
            
            # Find which month name is in the query
            for month_name, month_num in month_map.items():
                if month_name.lower() in query.lower():
                    time_filter = {
                        "filter_type": "month",
                        "month": month_num,
                        "year": current_year,  # Default to current year
                        "original_query": query,
                        "description": f"month {month_name} ({month_num}) of {current_year}"
                    }
                    break
        
        return time_filter

    def ask_with_rag(self, query: str):
        """Process the query using RAG and return the chatbot's response and source documents."""
        # Extract time filter information from the query
        time_filter = self.preprocess_time_query(query)
        
        # Retrieve documents with potential filtering based on time
        if time_filter:
            # Apply metadata filters for date-specific queries
            retrieved_docs = self.retrieve_with_date_filter(time_filter)
            print(f"Applied time filter for {time_filter['description']}, found {len(retrieved_docs)} docs")
        else:
            # Use standard retrieval for non-date queries
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
    
    def retrieve_with_date_filter(self, time_filter):
        """
        Retrieve documents from the vector store with date filtering.
        This ensures we only get documents from the specified time period.
        """
        # Get all nodes from the index
        all_nodes = self.index.docstore.docs.values()
        
        # Filter nodes based on time filter
        filtered_nodes = []
        
        for node in all_nodes:
            metadata = node.metadata
            
            # Check if this is a date-tagged document
            if 'year' in metadata and 'month' in metadata:
                # Filter by year only
                if time_filter['filter_type'] == 'year' and metadata['year'] == time_filter['year']:
                    filtered_nodes.append(node)
                
                # Filter by month and year
                elif (time_filter['filter_type'] == 'month' and 
                      metadata['month'] == time_filter['month'] and 
                      metadata['year'] == time_filter['year']):
                    filtered_nodes.append(node)
        
        # If we found date-filtered documents, return them
        if filtered_nodes:
            # Convert nodes back to retrieval format
            from llama_index.core.schema import NodeWithScore
            return [NodeWithScore(node=node, score=1.0) for node in filtered_nodes[:10]]
        
        # Fall back to semantic search if no date-filtered docs found
        query = time_filter['original_query']
        print(f"No exact date matches found, falling back to semantic search for: {query}")
        return self.query_engine.retrieve(query)

    def find_rag_document(self, query: str) -> list:
        """
        Process a query and return relevant document paths.
        Uses date filtering if the query contains time expressions.
        """
        # Extract time filter information from the query
        time_filter = self.preprocess_time_query(query)
        
        # Retrieve documents with potential filtering based on time
        if time_filter:
            # Apply metadata filters for date-specific queries
            retrieved_docs = self.retrieve_with_date_filter(time_filter)
            print(f"Applied time filter for {time_filter['description']}, found {len(retrieved_docs)} docs")
        else:
            # Use standard retrieval for non-date queries
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

        print(paths)
        return paths



# Create a chatbot instance for Flask to use
# chatbot = Chatbot(load_documents=True)
