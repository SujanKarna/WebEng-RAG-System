from typing import List

from src.config.settings import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT_TEMPLATE,
    RAG_MAX_CONTEXT_CHUNKS,
)

from src.retrieval.retrieval_models import RetrievedChunk


class PromptBuilder:
    """
    Builds grounded prompts from retrieved RAG chunks.
    """

    def __init__(
        self,
        max_context_chunks: int = RAG_MAX_CONTEXT_CHUNKS,
    ):
        self.max_context_chunks = max_context_chunks

    def build_context(
    self,
    chunks: List[RetrievedChunk],
) -> str:

        selected_chunks = chunks[
            : self.max_context_chunks
        ]

        context_parts = []

        for index, chunk in enumerate(
            selected_chunks,
            start=1,
        ):

            metadata = []

            if chunk.chunk_type:
                metadata.append(
                    f"Typ: {chunk.chunk_type}"
                )

            context = chunk.context or {}

            paragraph = context.get(
                "paragraph"
            )

            section = context.get(
                "section"
            )

            module = context.get(
                "module"
            )

            title = context.get(
                "title"
            )

            if paragraph:
                metadata.append(
                    f"Paragraph: {paragraph}"
                )

            if section:
                metadata.append(
                    f"Abschnitt: {section}"
                )

            if module:
                metadata.append(
                    f"Modul: {module}"
                )

            if title:
                metadata.append(
                    f"Titel: {title}"
                )

            source_info = "\n".join(metadata)

            context_parts.append(
                f"""
    [QUELLE {index}]
    Source-ID: {chunk.chunk_id}
    Retrieval-Score: {chunk.score:.4f}
    {source_info}

    INHALT:
    {chunk.text}
    [/QUELLE {index}]
    """.strip()
            )

        return "\n\n".join(context_parts)

    def build(
        self,
        query: str,
        chunks: List[RetrievedChunk],
    ) -> tuple[str, str]:

        context = self.build_context(chunks)

        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            query=query,
            context=context,
        )

        return RAG_SYSTEM_PROMPT, user_prompt