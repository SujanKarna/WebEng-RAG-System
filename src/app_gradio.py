import gradio as gr
from src.helper_utils import word_wrap
from src.query_engine import (
    load_collection,
    login_to_hf,
    build_collection,
    answer_query
)

# build the collection once at startup
login_to_hf()
collection = load_collection()

def rag_search(query: str) -> str:
    if not query.strip():
        return "Please enter a valid query.\nBitte eine Frage eingeben."
    doc = answer_query(collection, query)
    if not doc:
        return "No relevant documents found.\nKeine relevanten Dokumente gefunden."
    wrapped_docs = [word_wrap(d, width=100) for d in doc]
    return "\n\n---\n\n".join(wrapped_docs)

with gr.Blocks(title="TUC WebEngineering RAG Search") as demo:
    gr.Markdown("# TUC WebEngineering RAG Search\nAsk questions about the course materials.")
    with gr.Row():
        query_box = gr.Textbox(label="Enter your query", placeholder="e.g., What is the module number of Current Trends in Web Engineering?", lines=2)
    output_box = gr.Textbox(label="Retrieved Documents", lines=20, interactive=False)
    search_button = gr.Button("Search")
    search_button.click(fn=rag_search, inputs=query_box, outputs=output_box)

if __name__ == "__main__":    demo.launch()