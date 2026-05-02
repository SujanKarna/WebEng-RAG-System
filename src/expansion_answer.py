# import necessary libraries
from huggingface_hub import login
from helper_utils import word_wrap
from pypdf import PdfReader
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

login(token=hf_token)


# read the pdf file and extract the text
reader = PdfReader("data/AB_31_2015Teil1.pdf")
pdf_texts = [p.extract_text() for p in reader.pages]

# filter the empty pages
pdf_texts = [text for text in pdf_texts if text]

# print the first page of the pdf
# print(
#     word_wrap(pdf_texts[0], width=100)
# )

# split the text into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

character_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", "", ". "],
    chunk_size=1000, chunk_overlap=0)

character_split_texts = character_splitter.split_text("\n\n".join(pdf_texts))
# print(word_wrap(character_split_texts[9]))
# print(f"Number of chunks: {len(character_split_texts)}")

#split the chunks into tokens
token_splitter = SentenceTransformersTokenTextSplitter(
    chunk_overlap= 0, tokens_per_chunk= 256
)

token_split_texts = []
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)
# print(word_wrap(token_split_texts[9]))
# print(f"Number of chunks: {len(token_split_texts)}")



import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_function = SentenceTransformerEmbeddingFunction(model_name="intfloat/multilingual-e5-base")
# print(embedding_function([token_split_texts[9]]))

chroma_client = chromadb.Client()
chroma_collection = chroma_client.create_collection(name="german_pdf_chunks", embedding_function=embedding_function)

ids = [str(i) for i in range(len(token_split_texts))]
chroma_collection.add(
    documents=token_split_texts,
    ids=ids
)
print(chroma_collection.count())

query = "wie lautet die Modulnummer für Current Trends in Web Engineering?"
results = chroma_collection.query(
    query_texts=[query],
    n_results=3
)
retrieved_documents = results['documents'][0]
for doc in retrieved_documents:
    print(word_wrap(doc))
    print("\n---\n")