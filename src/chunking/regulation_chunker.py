from typing import Any, Dict, List
import re


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum approximate character size for a regulation chunk.
#
# We deliberately use characters rather than tokens here.
# Token-aware splitting can be introduced later if necessary.
#
# Most regulations will remain intact because they are already
# semantically meaningful units.
MAX_REGULATION_CHARS = 3500


# Module fields that deserve independent retrieval chunks.
#
# These are intentionally semantic fields rather than arbitrary
# text windows.
MODULE_FIELDS = [
    ("content", "Content"),
    ("qualification_goals", "Qualification Goals"),
    ("teaching_forms", "Teaching Forms"),
    ("prerequisites", "Prerequisites"),
    ("applicability", "Applicability"),
    ("credit_requirements", "Credit Requirements"),
    ("examination", "Examination"),
    ("credits_and_grades", "Credits and Grades"),
    ("frequency", "Frequency"),
    ("workload", "Workload"),
    ("duration", "Duration"),
]


# ============================================================
# PUBLIC API
# ============================================================

def chunk_regulation(
    regulation: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Convert the structured regulation JSON into semantic
    RAG-ready chunks.

    The TOC is intentionally NOT chunked.

    Chunk strategy
    --------------

    Regulation paragraphs:
        - Small paragraphs remain intact.
        - Large paragraphs are split semantically.

    Module sections:
        - The module-selection information is chunked separately.
        - PDF header/footer artifacts are removed.

    Module descriptions:
        - Each meaningful module field becomes its own chunk.
        - This improves retrieval for targeted questions such as:
            "What are the prerequisites?"
            "How is the module examined?"
            "How many credits does it have?"

    Every chunk receives provenance metadata so that the final
    RAG answer can cite the original regulation and page range.
    """

    chunks: List[Dict[str, Any]] = []

    chunk_index = 0

    for part in regulation.get("parts", []):

        part_name = part.get("part")
        part_title = part.get("title")

        for regulation_section in part.get(
            "regulations",
            [],
        ):

            paragraph = regulation_section.get("paragraph")
            paragraph_title = regulation_section.get("title")

            # ====================================================
            # 1. REGULATION PARAGRAPH
            # ====================================================

            blocks = regulation_section.get(
                "blocks",
                [],
            )

            regulation_chunks = _build_regulation_chunks(
                blocks=blocks,
                part_name=part_name,
                part_title=part_title,
                paragraph=paragraph,
                paragraph_title=paragraph_title,
            )

            for chunk in regulation_chunks:

                chunk["chunk_index"] = chunk_index

                chunks.append(chunk)

                chunk_index += 1

            # ====================================================
            # 2. MODULE SECTIONS
            # ====================================================

            for module_section in regulation_section.get(
                "module_sections",
                [],
            ):

                section_number = module_section.get(
                    "number"
                )

                section_title = module_section.get(
                    "title"
                )

                # ------------------------------------------------
                # Module selection information
                # ------------------------------------------------

                module_section_chunks = _build_module_section_chunks(
                    blocks=module_section.get(
                        "blocks",
                        [],
                    ),
                    part_name=part_name,
                    part_title=part_title,
                    paragraph=paragraph,
                    paragraph_title=paragraph_title,
                    section_number=section_number,
                    section_title=section_title,
                )

                for chunk in module_section_chunks:

                    chunk["chunk_index"] = chunk_index

                    chunks.append(chunk)

                    chunk_index += 1

                # ------------------------------------------------
                # Module descriptions
                # ------------------------------------------------

                for module in module_section.get(
                    "modules",
                    [],
                ):

                    module_chunks = _build_module_chunks(
                        module=module,
                        part_name=part_name,
                        part_title=part_title,
                        paragraph=paragraph,
                        paragraph_title=paragraph_title,
                        section_number=section_number,
                        section_title=section_title,
                    )

                    for chunk in module_chunks:

                        chunk["chunk_index"] = chunk_index

                        chunks.append(chunk)

                        chunk_index += 1

    return chunks


# ============================================================
# REGULATION CHUNKS
# ============================================================

def _build_regulation_chunks(
    blocks: List[Dict[str, Any]],
    part_name: str,
    part_title: str,
    paragraph: str,
    paragraph_title: str,
) -> List[Dict[str, Any]]:
    """
    Convert the blocks belonging to one regulation paragraph
    into semantic chunks.

    Important:

    We do NOT create one chunk per PDF block.

    Instead, blocks are first cleaned and combined. This prevents
    PDF layout boundaries from becoming artificial semantic
    boundaries.
    """

    valid_blocks = []

    for block in blocks:

        text = _clean_pdf_artifacts(
            block.get("text", "")
        )

        if not text:
            continue

        valid_blocks.append(
            {
                "text": text,
                "page": block.get("page_number"),
                "block_index": block.get("block_index"),
                "zone": block.get("zone"),
            }
        )

    if not valid_blocks:
        return []

    # ------------------------------------------------------------
    # Combine consecutive blocks.
    # ------------------------------------------------------------

    combined_text = "\n\n".join(
        block["text"]
        for block in valid_blocks
    )

    page_start = _first_page(valid_blocks)
    page_end = _last_page(valid_blocks)

    # ------------------------------------------------------------
    # Small paragraph:
    # keep the entire paragraph as one chunk.
    # ------------------------------------------------------------

    if len(combined_text) <= MAX_REGULATION_CHARS:

        return [
            {
                "chunk_id": _paragraph_chunk_id(
                    paragraph
                ),

                "chunk_type": "regulation",

                "text": _make_regulation_header(
                    paragraph=paragraph,
                    paragraph_title=paragraph_title,
                    text=combined_text,
                ),

                "metadata": {
                    "part": part_name,
                    "part_title": part_title,

                    "paragraph": paragraph,
                    "paragraph_title": paragraph_title,

                    "page_start": page_start,
                    "page_end": page_end,

                    "zone": "main_regulations",

                    "source_type": "regulation",
                },
            }
        ]

    # ------------------------------------------------------------
    # Large paragraph:
    # split semantically.
    # ------------------------------------------------------------

    semantic_parts = _split_large_regulation(
        combined_text
    )

    chunks = []

    for index, text in enumerate(
        semantic_parts
    ):

        chunks.append(
            {
                "chunk_id": (
                    f"{_paragraph_chunk_id(paragraph)}"
                    f"_{index:02d}"
                ),

                "chunk_type": "regulation",

                "text": _make_regulation_header(
                    paragraph=paragraph,
                    paragraph_title=paragraph_title,
                    text=text,
                ),

                "metadata": {
                    "part": part_name,
                    "part_title": part_title,

                    "paragraph": paragraph,
                    "paragraph_title": paragraph_title,

                    "page_start": page_start,
                    "page_end": page_end,

                    "zone": "main_regulations",

                    "source_type": "regulation",

                    "semantic_part": index,
                },
            }
        )

    return chunks


# ============================================================
# LARGE REGULATION SPLITTING
# ============================================================

def _split_large_regulation(
    text: str,
) -> List[str]:
    """
    Split a large regulation into meaningful units.

    Priority:

        1. numbered subsections: (1), (2), ...
        2. numbered lists: 1., 2., ...
        3. paragraph boundaries
        4. character limit as final fallback
    """

    # ------------------------------------------------------------
    # Split on German legal subsections.
    #
    # Example:
    #
    # (1) ...
    # (2) ...
    # (3) ...
    # ------------------------------------------------------------

    matches = list(
        re.finditer(
            r"(?m)(?=^\(\d+\))",
            text,
        )
    )

    if len(matches) > 1:

        parts = []

        for index, match in enumerate(matches):

            start = match.start()

            if index + 1 < len(matches):

                end = matches[
                    index + 1
                ].start()

            else:

                end = len(text)

            part = text[
                start:end
            ].strip()

            if part:
                parts.append(part)

        if parts:

            return _merge_small_parts(
                parts
            )

    # ------------------------------------------------------------
    # Fallback:
    # split by paragraphs.
    # ------------------------------------------------------------

    paragraphs = [
        part.strip()
        for part in re.split(
            r"\n\s*\n",
            text,
        )
        if part.strip()
    ]

    if len(paragraphs) > 1:

        return _merge_small_parts(
            paragraphs
        )

    # ------------------------------------------------------------
    # Final fallback:
    # hard split by characters.
    # ------------------------------------------------------------

    return _hard_split(
        text,
        MAX_REGULATION_CHARS,
    )


def _merge_small_parts(
    parts: List[str],
) -> List[str]:
    """
    Merge small semantic parts so that we don't create
    unnecessarily tiny chunks.
    """

    chunks = []

    current = ""

    for part in parts:

        if not current:

            current = part
            continue

        candidate = (
            current
            + "\n\n"
            + part
        )

        if len(candidate) <= MAX_REGULATION_CHARS:

            current = candidate

        else:

            chunks.append(current)

            current = part

    if current:
        chunks.append(current)

    return chunks


def _hard_split(
    text: str,
    max_chars: int,
) -> List[str]:
    """
    Last-resort character split.

    Tries to split at sentence boundaries before falling
    back to a hard character boundary.
    """

    chunks = []

    remaining = text.strip()

    while len(remaining) > max_chars:

        candidate = remaining[
            :max_chars
        ]

        # Prefer sentence boundary.
        split_position = candidate.rfind(
            ". "
        )

        # Then newline.
        if split_position < max_chars * 0.5:

            split_position = candidate.rfind(
                "\n"
            )

        # Final fallback.
        if split_position < max_chars * 0.5:

            split_position = max_chars

        chunk = remaining[
            :split_position
        ].strip()

        if chunk:
            chunks.append(chunk)

        remaining = remaining[
            split_position:
        ].strip()

    if remaining:
        chunks.append(remaining)

    return chunks


# ============================================================
# MODULE SECTION CHUNKS
# ============================================================

def _build_module_section_chunks(
    blocks: List[Dict[str, Any]],
    part_name: str,
    part_title: str,
    paragraph: str,
    paragraph_title: str,
    section_number: Any,
    section_title: str,
) -> List[Dict[str, Any]]:
    """
    Build chunks for the module-selection portion of §6.

    Example:

        Grundlagenmodule
        Vertiefungsmodule
        Module Schlüsselkompetenzen
        Forschungsseminar
        Challengemodule
        Master-Arbeit

    PDF headers and page numbers are removed.
    """

    valid_blocks = []

    for block in blocks:

        text = _clean_pdf_artifacts(
            block.get("text", "")
        )

        if not text:
            continue

        valid_blocks.append(
            {
                "text": text,
                "page": block.get("page_number"),
                "block_index": block.get("block_index"),
                "zone": block.get("zone"),
            }
        )

    if not valid_blocks:
        return []

    text = "\n\n".join(
        block["text"]
        for block in valid_blocks
    )

    if not text.strip():
        return []

    return [
        {
            "chunk_id": (
                "module_section_"
                f"{section_number}"
            ),

            "chunk_type": "module_section",

            "text": (
                f"§ {paragraph.lstrip('§ ').strip()}"
                f" – {section_title}\n\n"
                f"{text}"
            ),

            "metadata": {
                "part": part_name,
                "part_title": part_title,

                "paragraph": paragraph,
                "paragraph_title": paragraph_title,

                "section_number": section_number,
                "section_title": section_title,

                "page_start": _first_page(
                    valid_blocks
                ),

                "page_end": _last_page(
                    valid_blocks
                ),

                "zone": "main_regulations",

                "source_type": "module_selection",
            },
        }
    ]


# ============================================================
# MODULE DESCRIPTION CHUNKS
# ============================================================

def _build_module_chunks(
    module: Dict[str, Any],
    part_name: str,
    part_title: str,
    paragraph: str,
    paragraph_title: str,
    section_number: Any,
    section_title: str,
) -> List[Dict[str, Any]]:
    """
    Create semantic chunks from one module description.

    Each meaningful module field becomes an independent retrieval
    unit.

    This is particularly useful for targeted student questions.
    """

    module_code = module.get(
        "module_code"
    )

    module_name = module.get(
        "module_name"
    )

    description = module.get(
        "description"
    )

    if not description:
        return []

    sources = module.get(
        "sources",
        {}
    )

    module_source = sources.get(
        "module_description",
        {}
    )

    chunks = []

    for field_name, field_title in MODULE_FIELDS:

        value = description.get(
            field_name
        )

        if not value:
            continue

        value = str(value).strip()

        if not value:
            continue

        # --------------------------------------------------------
        # Self-contained text.
        #
        # We repeat the module identity in every chunk because
        # embeddings should understand what the field belongs to
        # even when the chunk is retrieved independently.
        # --------------------------------------------------------

        text_parts = []

        if module_name:

            text_parts.append(
                f"Module: {module_name}"
            )

        if module_code:

            text_parts.append(
                f"Module Code: {module_code}"
            )

        text_parts.append(
            f"{field_title}:\n{value}"
        )

        module_text = "\n\n".join(
            text_parts
        )

        chunk_id = (
            f"module_{module_code}_"
            f"{field_name}"
        )

        chunks.append(
            {
                "chunk_id": chunk_id,

                "chunk_type": "module_field",

                "text": module_text,

                "metadata": {
                    "part": part_name,
                    "part_title": part_title,

                    "paragraph": paragraph,
                    "paragraph_title": paragraph_title,

                    "section_number": section_number,
                    "section_title": section_title,

                    "module_code": module_code,
                    "module_name": module_name,

                    "field": field_name,

                    "credits": module.get(
                        "credits"
                    ),

                    "module_type": module.get(
                        "type"
                    ),

                    "page_start": module_source.get(
                        "start_page"
                    ),

                    "page_end": module_source.get(
                        "end_page"
                    ),

                    "zone": module_source.get(
                        "zone"
                    ),

                    "source_type": "module_description",
                },
            }
        )

    return chunks


# ============================================================
# PDF ARTIFACT REMOVAL
# ============================================================

def _clean_pdf_artifacts(
    text: str,
) -> str:
    """
    Remove obvious PDF headers, footers and page-number artifacts.

    This is intentionally conservative.

    We do not perform aggressive linguistic cleaning here because
    the regulation text itself must remain faithful to the source.
    """

    if not text:
        return ""

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        normalized = line.strip()

        if not normalized:
            continue

        # --------------------------------------------------------
        # Official publication header.
        # --------------------------------------------------------

        if normalized == "Amtliche Bekanntmachungen":
            continue

        # --------------------------------------------------------
        # Horizontal separator.
        # --------------------------------------------------------

        if re.fullmatch(
            r"[_\-]{5,}",
            normalized,
        ):
            continue

        # --------------------------------------------------------
        # Publication number.
        # --------------------------------------------------------

        if re.fullmatch(
            r"Nr\.\s*\d+/\d{4}",
            normalized,
        ):
            continue

        # --------------------------------------------------------
        # Publication date.
        # --------------------------------------------------------

        if re.fullmatch(
            r"vom\s+\d{1,2}\.\s+\w+\s+\d{4}",
            normalized,
        ):
            continue

        # --------------------------------------------------------
        # Standalone page numbers.
        #
        # We only remove pure numeric lines with a reasonable
        # page-number shape.
        # --------------------------------------------------------

        if re.fullmatch(
            r"\d{3,4}",
            normalized,
        ):
            continue

        cleaned_lines.append(
            normalized
        )

    return "\n".join(
        cleaned_lines
    ).strip()


# ============================================================
# TEXT HELPERS
# ============================================================

def _make_regulation_header(
    paragraph: str,
    paragraph_title: str,
    text: str,
) -> str:
    """
    Make every regulation chunk self-contained.

    This helps embeddings understand the context even when the
    chunk is retrieved without neighbouring chunks.
    """

    header = []

    if paragraph:
        header.append(
            paragraph
        )

    if paragraph_title:
        header.append(
            paragraph_title
        )

    if header:

        return (
            "\n".join(header)
            + "\n\n"
            + text
        )

    return text


def _paragraph_chunk_id(
    paragraph: str,
) -> str:
    """
    Convert § 6 into a stable identifier.
    """

    if not paragraph:

        return "regulation_unknown"

    number = re.sub(
        r"[^0-9A-Za-z]+",
        "_",
        paragraph,
    ).strip("_")

    return f"regulation_{number}"


def _first_page(
    blocks: List[Dict[str, Any]],
):
    """
    Return the first available page number.
    """

    pages = [
        block.get("page")
        for block in blocks
        if block.get("page") is not None
    ]

    return min(pages) if pages else None


def _last_page(
    blocks: List[Dict[str, Any]],
):
    """
    Return the last available page number.
    """

    pages = [
        block.get("page")
        for block in blocks
        if block.get("page") is not None
    ]

    return max(pages) if pages else None