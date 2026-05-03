import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
PDF_PATH = os.getenv("PDF_PATH", "data/AB_31_2015Teil1.pdf")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "german_pdf_chunks")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-base")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 0))
TOKENS_PER_CHUNK = int(os.getenv("TOKENS_PER_CHUNK", 256))
N_RESULTS = int(os.getenv("N_RESULTS", 3))
