from src.helper_utils import word_wrap
from src.query_engine import (
    login_to_hf,
    build_collection,
    answer_query
)

def main():
    # Step 1: Log in to Hugging Face Hub
    login_to_hf()
    
    # Step 2: Build the vector store collection from the PDF documents
    collection = build_collection()
    
    # Step 3: Query the collection and print the results
    query = "module number of Current Trends in Web Engineering?"
    retrieved_docs = answer_query(collection, query)
    
    print("Retrieved Documents:")
    for doc in retrieved_docs:
        print(word_wrap(doc, width=80),end="\n\n")
       

if __name__ == "__main__":    main()