from src.ingest_pdf import load_pdf_texts
from src.chunking import character_split, token_split
from src.vectorstore import create_chroma_collection, add_documents_to_collection
from src.config import (
    PDF_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOKENS_PER_CHUNK,
)
import os


def build_collection():
    print("Loading PDF(s)...")
    pdf_texts = load_pdf_texts(PDF_PATH)

    print("Chunking text...")
    char_chunks = character_split(pdf_texts, CHUNK_SIZE, CHUNK_OVERLAP)
    token_chunks = token_split(char_chunks, TOKENS_PER_CHUNK, CHUNK_OVERLAP)

    print("Creating/loading Chroma collection...")
    collection = create_chroma_collection(COLLECTION_NAME, EMBEDDING_MODEL_NAME)

    print("Adding documents (with stable IDs)...")
    source_name = os.path.basename(PDF_PATH)
    add_documents_to_collection(collection, token_chunks, source_name=source_name)

    print("Vectorstore built successfully.")
    return collection


if __name__ == "__main__":
    build_collection()
