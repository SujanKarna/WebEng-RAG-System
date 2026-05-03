from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

# Splits the text into smaller chunks based on characters and tokens
def character_split(texts: List[str], chunk_size: int = 1000, chunk_overlap: int = 0) -> List[str]:
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", "", ". "],
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    character_split_texts = []
    for text in texts:
        character_split_texts += character_splitter.split_text(text)
    return character_split_texts

# Splits the character chunks into smaller chunks based on tokens
def token_split(character_chunks: List[str], token_per_chunk: int = 256, chunk_overlap: int = 0) -> List[str]:
    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap= chunk_overlap, tokens_per_chunk= token_per_chunk
    )
    token_split_texts = []
    for text in character_chunks:
        token_split_texts += token_splitter.split_text(text)
    return token_split_texts