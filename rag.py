import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI

LOAD_DOCUMENTS = True
QUERY = "What is the definition of embeddings in the context of LLMs?"

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("tech16example")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Create Vector index
if LOAD_DOCUMENTS:
  documents = SimpleDirectoryReader("./test_data/obsidian", required_exts=[".md"], recursive=True).load_data()
  index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
else:
  # load only existing embeddings from ChromaDB
  index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

# Create query engine
query_engine = index.as_query_engine()

# Retrieve matching documents based on query
retrieved_docs = query_engine.retrieve(QUERY)
for doc in retrieved_docs:
    print(f"Document: {doc.metadata.get('file_path', 'Unknown')}\nScore: {doc.score}\n")

# Extract text content from selected documents
context_text = "\n\n".join(doc.text for doc in retrieved_docs)

Settings.llm = OpenAI(model="gpt-3.5-turbo", temperatur=0.7)
# Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
# Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
# Settings.num_output = 512
# Settings.context_window = 3900

# Generate response using LLM with custom context
prompt = f"Using the following documents, answer the query: '{QUERY}'\n\n{context_text}"
response = Settings.llm.complete(prompt)

print(response)
