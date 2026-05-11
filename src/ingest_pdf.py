# Reading and Extracting text from PDF file
from pypdf import PdfReader
from typing import List

def load_pdf_texts(pdf_path: str) -> List[str]:
    # read the pdf file
    reader = PdfReader(pdf_path)
    texts = []
    # extract the text from each page
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            texts.append(text)
    
    return texts