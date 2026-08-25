from typing import Any, Dict, List

from src.chunking.chunk_models import Chunk
from src.chunking.context_builder import (
    DOCUMENT_ID,
    build_regulation_context,
    build_section_context,
)


def _build_paragraph_text(
    paragraph: Dict[str, Any],
) -> str:

    parts = []

    if paragraph.get("paragraph"):
        parts.append(
            f"{paragraph['paragraph']}: "
            f"{paragraph.get('paragraph_title', '')}".strip()
        )

    text = paragraph.get("text")

    if text:
        parts.append(text.strip())

    return "\n\n".join(parts).strip()


def chunk_main_regulation(
    regulation: List[Dict[str, Any]],
) -> List[Chunk]:
    """
    Convert normalized main regulation into semantic chunks.

    Each paragraph remains a semantic unit.

    §6 receives additional structured chunks for its
    curriculum sections and module references.
    """

    chunks: List[Chunk] = []

    for paragraph in regulation:

        paragraph_number = paragraph.get(
            "paragraph"
        )

        # ----------------------------------------------------
        # §6
        # ----------------------------------------------------

        if paragraph_number == "§ 6":

            sections = paragraph.get(
                "sections",
                [],
            )

            for section in sections:

                section_number = section.get(
                    "number"
                )

                section_title = section.get(
                    "title"
                )

                text = section.get(
                    "text",
                    "",
                ).strip()

                context = build_section_context(
                    paragraph,
                    section,
                )

                chunks.append(
                    Chunk(
                        chunk_id=(
                            f"regulation_"
                            f"{paragraph_number}_"
                            f"section_{section_number}"
                        ),
                        chunk_index=len(chunks),
                        document_id=DOCUMENT_ID,
                        chunk_type="regulation_section",
                        text=(
                            f"{paragraph_number} "
                            f"{paragraph.get('paragraph_title', '')}\n\n"
                            f"Section {section_number}: "
                            f"{section_title}\n\n"
                            f"{text}"
                        ).strip(),
                        context=context,
                        zone="main_regulation",
                    )
                )

            continue

        # ----------------------------------------------------
        # Normal paragraph
        # ----------------------------------------------------

        text = _build_paragraph_text(
            paragraph
        )

        if not text:
            continue

        chunks.append(
            Chunk(
                chunk_id=(
                    f"regulation_"
                    f"{paragraph_number}"
                ),
                chunk_index=len(chunks),
                document_id=DOCUMENT_ID,
                chunk_type="regulation_paragraph",
                text=text,
                context=build_regulation_context(
                    paragraph
                ),
                zone="main_regulation",
            )
        )

    return chunks