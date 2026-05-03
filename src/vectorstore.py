# Vector Store Implementation -> converting tokens into embeddings and storing them in a vector database i.e chromadb
from typing import List
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction # Embedding function to convert text into embeddings using sentence transformers

# Create a chroma collection with the specified embedding function
def create_chroma_collection(collection_name: str, embedding_model_name: str):
    embedding_function = SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    chroma_collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=embedding_function)
    return chroma_collection

# Add documents to the chroma collection
def add_documents_to_collection(collection, documents: List[str]):
    ids = [str(i) for i in range(len(documents))]
    collection.add(
        documents=documents,
        ids=ids
    )
    return collection

# Query the chroma collection to retrieve relevant documents based on a query
def query_collection(collection, query: str, n_results: int = 5):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    retrieved_documents = results['documents'][0]
    return retrieved_documents