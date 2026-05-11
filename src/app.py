import os
import gradio as gr
from src.helper_utils import word_wrap
from src.query_engine import (
    load_collection,
    answer_with_rag
)

# build the collection once at startup
os.environ["HF_SPACE"] = "1"  # Set this to "1" to indicate we're running in a Hugging Face Space
collection = load_collection()

def rag_search(query: str):
    if not query.strip():
        return "Please enter a valid query.\nBitte eine Frage eingeben.", ""
    answer, docs = answer_with_rag(collection, query)
    wrapped_docs = [word_wrap(d, width=100) for d in docs]
    print("DEBUG: Query =", query)
    print("DEBUG: Retrieved docs =", docs)
    print("DEBUG: Answer =", answer)

    return answer, "\n\n---\n\n".join(wrapped_docs)

with gr.Blocks(title="TUC WebEngineering RAG Search") as demo:
    gr.Markdown("# TUC WebEngineering RAG Search\nAsk questions about the course materials.")
    gr.Markdown(
    "### ℹ️ This RAG system currently uses the **2015 Web Engineering Study Regulation** (AB 31/2015). "
    "More documents and updated regulations will be added soon. The system is still under active development."
)

    with gr.Row():
        query_box = gr.Textbox(
            label="Enter your query", 
            placeholder="e.g., What is the module number of Current Trends in Web Engineering?", 
            lines=2
            )
    answer_box = gr.Textbox(label="Answer", lines=6, interactive=False)
    retrieved_box = gr.Textbox(label="Retrieved Documents", lines=18, interactive=False)
    search_button = gr.Button("Search")
    search_button.click(
        fn=rag_search, 
        inputs=query_box, 
        outputs=[answer_box, retrieved_box],
        )

if __name__ == "__main__":    demo.launch()