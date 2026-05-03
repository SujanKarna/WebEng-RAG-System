# Reading and Extracting text from PDF file
from pypdf import PdfReader
from typing import List

def load_pdf_texts(pdf_path: str) -> List[str]:
    # read the pdf file
    reader = PdfReader(pdf_path)
    # extract the text from each page
    pdf_texts = [p.extract_text() for p in reader.pages]
    # filter the empty pages
    pdf_texts = [text for text in pdf_texts if text]
    return pdf_texts