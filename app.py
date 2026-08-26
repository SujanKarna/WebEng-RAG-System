import re

import gradio as gr

from src.generation.rag_pipeline import RAGPipeline


# ============================================================
# CONFIGURATION
# ============================================================

INDEX_DIRECTORY = "data/processed/faiss_index"

TOP_K = 5


# ============================================================
# INITIALIZE RAG PIPELINE
# ============================================================

print("=" * 80)
print("INITIALIZING WEB ENGINEERING RAG")
print("=" * 80)

rag_pipeline = RAGPipeline(
    index_directory=INDEX_DIRECTORY
)

print("RAG pipeline initialized.")
print("=" * 80)


# ============================================================
# SOURCE CITATION NORMALIZATION
# ============================================================

def normalize_source_citations(
    text: str,
) -> str:
    """
    Normalize different citation formats generated
    by the LLM to the format used by the application.

    Examples:
        [SOURCE 1] -> [Quelle 1]
        [Source 2] -> [Quelle 2]
        [source 3] -> [Quelle 3]
    """

    return re.sub(
        r"\[(?:SOURCE|Source|source)\s+(\d+)\]",
        r"[Quelle \1]",
        text,
    )


# ============================================================
# BUILD SOURCE DISPLAY
# ============================================================

def build_source_display(
    sources,
) -> str:
    """
    Build a human-readable source section from the
    actual RetrievedChunk objects returned by the retriever.
    """

    if not sources:
        return (
            "### 📚 Quellen\n\n"
            "Keine Quellen verfügbar."
        )

    output = [
        "### 📚 Quellen",
        "",
        "Die folgenden Quellen wurden tatsächlich "
        "für diese Antwort abgerufen:",
        "",
    ]

    for index, chunk in enumerate(
        sources,
        start=1,
    ):

        # ----------------------------------------------------
        # Basic metadata
        # ----------------------------------------------------

        chunk_type = (
            chunk.chunk_type
            if chunk.chunk_type
            else "Unbekannt"
        )

        chunk_id = (
            chunk.chunk_id
            if chunk.chunk_id
            else "Unbekannt"
        )

        # ----------------------------------------------------
        # Page information
        # ----------------------------------------------------

        if (
            chunk.page_start is not None
            and chunk.page_end is not None
        ):

            if chunk.page_start == chunk.page_end:
                pages = f"Seite {chunk.page_start}"

            else:
                pages = (
                    f"Seiten "
                    f"{chunk.page_start}–"
                    f"{chunk.page_end}"
                )

        elif chunk.page_start is not None:

            pages = f"Seite {chunk.page_start}"

        else:

            pages = "Seitenangabe nicht verfügbar"

        # ----------------------------------------------------
        # Context
        # ----------------------------------------------------

        context = (
            chunk.context
            if isinstance(
                chunk.context,
                dict,
            )
            else {}
        )

        paragraph = context.get(
            "paragraph"
        )

        paragraph_title = context.get(
            "paragraph_title"
        )

        section = context.get(
            "section"
        )

        section_title = context.get(
            "section_title"
        )

        module_code = context.get(
            "module_code"
        )

        module_name = context.get(
            "module_name"
        )

        # ----------------------------------------------------
        # Build source title
        # ----------------------------------------------------

        title_parts = []

        if module_code:

            module_title = (
                f"{module_code}"
            )

            if module_name:

                module_title += (
                    f" — {module_name}"
                )

            title_parts.append(
                module_title
            )

        elif paragraph:

            paragraph_title_text = (
                f"§ {paragraph}"
            )

            if paragraph_title:

                paragraph_title_text += (
                    f" — {paragraph_title}"
                )

            title_parts.append(
                paragraph_title_text
            )

        elif section:

            section_text = (
                f"Section {section}"
            )

            if section_title:

                section_text += (
                    f" — {section_title}"
                )

            title_parts.append(
                section_text
            )

        else:

            title_parts.append(
                chunk_id
            )

        source_title = " | ".join(
            title_parts
        )

        # ----------------------------------------------------
        # Source block
        # ----------------------------------------------------

        output.append(
            f"#### Quelle {index}"
        )

        output.append(
            f"**{source_title}**"
        )

        output.append(
            f"- Typ: `{chunk_type}`"
        )

        output.append(
            f"- {pages}"
        )

        output.append("")

        # ----------------------------------------------------
        # Source text
        # ----------------------------------------------------

        source_text = (
            chunk.text
            if chunk.text
            else ""
        )

        if source_text:

            output.append(
                f"> {source_text.replace(chr(10), ' ')}"
            )

        output.append("")

        output.append("---")

        output.append("")

    return "\n".join(
        output
    )


# ============================================================
# ANSWER FUNCTION
# ============================================================

def answer_question(
    question: str,
):
    """
    Run the RAG pipeline and return:

        1. Generated answer
        2. Actual retrieved sources
    """

    if (
        not question
        or not question.strip()
    ):

        return (
            "Bitte geben Sie eine Frage ein.",
            "### 📚 Quellen\n\n"
            "Keine Frage gestellt.",
        )

    try:

        # ----------------------------------------------------
        # Retrieve answer + actual source chunks
        # ----------------------------------------------------

        answer_text, sources = (
            rag_pipeline.answer_with_sources(
                query=question.strip(),
                top_k=TOP_K,
            )
        )

        # ----------------------------------------------------
        # Normalize LLM citations
        # ----------------------------------------------------

        answer_text = (
            normalize_source_citations(
                answer_text
            )
        )

        # ----------------------------------------------------
        # Build source section
        # ----------------------------------------------------

        source_text = (
            build_source_display(
                sources
            )
        )

        return (
            answer_text,
            source_text,
        )

    except Exception as error:

        print(
            f"ERROR: {error}"
        )

        return (
            "Bei der Verarbeitung Ihrer Frage "
            "ist ein Fehler aufgetreten.",
            (
                "### 📚 Quellen\n\n"
                "Die Quellen konnten nicht "
                "angezeigt werden."
            ),
        )


# ============================================================
# GRADIO UI
# ============================================================

with gr.Blocks(
    title="Web Engineering RAG",
) as demo:

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    gr.Markdown(
        """
        # 🎓 2025 Web Engineering Study Regulation Assistant

        Ask questions about the **Master's degree programme
        Web Engineering at TU Chemnitz**.

        The answers are generated exclusively from the
        provided study regulation and module descriptions.
        """
    )

    # --------------------------------------------------------
    # Examples
    # --------------------------------------------------------

    gr.Markdown(
        """
        ### 💡 Example questions

        - Welche Voraussetzungen gelten für die Zulassung?
        - Wie lange dauert das Studium?
        - Welche Module gehören zu den Grundlagenmodulen?
        - Was lernt man im Modul Advanced Management of Data?
        - Was gilt für ein Teilzeitstudium?
        """
    )

    # --------------------------------------------------------
    # Question input
    # --------------------------------------------------------

    question = gr.Textbox(
        label="Ihre Frage",
        placeholder=(
            "Stellen Sie eine Frage zur Studienordnung..."
        ),
        lines=2,
    )

    # --------------------------------------------------------
    # Ask button
    # --------------------------------------------------------

    ask_button = gr.Button(
        "Frage beantworten",
        variant="primary",
    )

    # --------------------------------------------------------
    # Answer
    # --------------------------------------------------------

    gr.Markdown(
        "## 💬 Antwort"
    )

    answer = gr.Markdown()

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    source_output = gr.Markdown()

    # --------------------------------------------------------
    # Button event
    # --------------------------------------------------------

    ask_button.click(
        fn=answer_question,
        inputs=question,
        outputs=[
            answer,
            source_output,
        ],
    )

    # --------------------------------------------------------
    # Enter key event
    # --------------------------------------------------------

    question.submit(
        fn=answer_question,
        inputs=question,
        outputs=[
            answer,
            source_output,
        ],
    )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    gr.Markdown(
        """
        ---

        **Quelle:** Studienordnung und Modulbeschreibungen
        des Masterstudiengangs Web Engineering, TU Chemnitz.

        This application uses retrieval-augmented generation
        with BGE-M3 embeddings, FAISS vector search and a
        local language model.
        """
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    demo.launch()
