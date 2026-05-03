from huggingface_hub import login
from typing import List
from src.config import (
    HF_TOKEN,
    PDF_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOKENS_PER_CHUNK,
    N_RESULTS,
)
from src.ingest_pdf import load_pdf_texts
from src.chunking import character_split, token_split
from src.vectorstore import create_chroma_collection, add_documents_to_collection, query_collection

# Log in to Hugging Face Hub
def login_to_hf():
    if HF_TOKEN:
        login(HF_TOKEN)
    else:
        raise ValueError("HF_TOKEN is not set in the environment variables.")
    
def build_collection():
    pdf_texts = load_pdf_texts(PDF_PATH)
    char_chunks = character_split(pdf_texts, CHUNK_SIZE, CHUNK_OVERLAP)
    token_chunks = token_split(char_chunks, TOKENS_PER_CHUNK, CHUNK_OVERLAP)
    collection = create_chroma_collection(COLLECTION_NAME, EMBEDDING_MODEL_NAME)
    add_documents_to_collection(collection, token_chunks)
    return collection

def load_collection():
    return create_chroma_collection(
        collection_name=COLLECTION_NAME,
        embedding_model_name=EMBEDDING_MODEL_NAME,
    )

def answer_query(collection, query: str, n_results: int = N_RESULTS) -> List[str]:
    retrieved_docs = query_collection(collection, query, n_results)
    return retrieved_docs

