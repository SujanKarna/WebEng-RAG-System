from typing import Any, Dict, List, Optional
import re

from src.models.chunk import Chunk


# ============================================================
# FOOTER / DOCUMENT ARTIFACT FILTERING
# ============================================================

FOOTER_PATTERNS = [
    r"^Amtliche Bekanntmachungen$",
    r"^Nr\.\s*\d+/\d{4}$",
    r"^vom\s+\d{1,2}\.\s+\w+\s+\d{4}$",
    r"^[-_]{5,}$",
]


def is_footer_or_artifact(text: Optional[str]) -> bool:
    """
    Return True if the block contains only known PDF
    footer / publication artifacts.
    """

    if not text:
        return True

    normalized = " ".join(
        text.strip().split()
    )

    if not normalized:
        return True

    for pattern in FOOTER_PATTERNS:
        if re.fullmatch(
            pattern,
            normalized,
            flags=re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# STRUCTURAL TRANSITION FILTERING
# ============================================================

def is_part_transition(
    text: Optional[str],
) -> bool:
    """
    Detect blocks which only introduce the next Teil/Part.

    Example:

        Teil 2
        Aufbau und Inhalte des Studiums
    """

    if not text:
        return False

    normalized = " ".join(
        text.strip().split()
    )

    return bool(
        re.fullmatch(
            r"Teil\s+\d+\s+.+",
            normalized,
            flags=re.IGNORECASE
        )
    )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_chunk_text(text: Optional[str]) -> str:
    """
    Normalize whitespace while preserving paragraph structure.
    """

    if not text:
        return ""

    # Normalize Windows line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces around newlines
    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        lines.append(line)

    return "\n".join(lines).strip()


# ============================================================
# CONTEXT BUILDERS
# ============================================================

def build_regulation_context(
    part_name: Optional[str],
    part_title: Optional[str],
    paragraph: Optional[str],
    paragraph_title: Optional[str],
) -> Dict[str, Any]:

    context: Dict[str, Any] = {}

    if part_name is not None:
        context["part"] = part_name

    if part_title is not None:
        context["part_title"] = part_title

    if paragraph is not None:
        context["paragraph"] = paragraph

    if paragraph_title is not None:
        context["paragraph_title"] = paragraph_title

    return context


def build_section_context(
    part_name: Optional[str],
    part_title: Optional[str],
    paragraph: Optional[str],
    paragraph_title: Optional[str],
    section_number: Optional[Any],
    section_title: Optional[str],
) -> Dict[str, Any]:

    context = build_regulation_context(
        part_name=part_name,
        part_title=part_title,
        paragraph=paragraph,
        paragraph_title=paragraph_title,
    )

    if section_number is not None:
        context["section"] = section_number

    if section_title is not None:
        context["section_title"] = section_title

    return context


def build_module_context(
    part_name: Optional[str],
    part_title: Optional[str],
    paragraph: Optional[str],
    paragraph_title: Optional[str],
    section_number: Optional[Any],
    section_title: Optional[str],
    module_code: Optional[str],
    module_name: Optional[str],
    module_type: Optional[str],
    credits: Optional[Any],
) -> Dict[str, Any]:

    context = build_section_context(
        part_name=part_name,
        part_title=part_title,
        paragraph=paragraph,
        paragraph_title=paragraph_title,
        section_number=section_number,
        section_title=section_title,
    )

    if module_code is not None:
        context["module_code"] = module_code

    if module_name is not None:
        context["module_name"] = module_name

    if module_type is not None:
        context["module_type"] = module_type

    if credits is not None:
        context["credits"] = credits

    return context


# ============================================================
# CONTEXT-AWARE TEXT
# ============================================================

def add_regulation_context_to_text(
    text: str,
    part_name: Optional[str],
    part_title: Optional[str],
    paragraph: Optional[str],
    paragraph_title: Optional[str],
) -> str:

    context_lines = []

    if part_name and part_title:
        context_lines.append(
            f"Part {part_name}: {part_title}"
        )
    elif part_name:
        context_lines.append(
            f"Part {part_name}"
        )

    if paragraph and paragraph_title:
        context_lines.append(
            f"{paragraph} {paragraph_title}"
        )
    elif paragraph:
        context_lines.append(
            paragraph
        )

    context_text = "\n".join(context_lines)

    if not context_text:
        return text

    return (
        f"{context_text}\n\n"
        f"{text}"
    ).strip()


def add_section_context_to_text(
    text: str,
    part_name: Optional[str],
    part_title: Optional[str],
    paragraph: Optional[str],
    paragraph_title: Optional[str],
    section_number: Optional[Any],
    section_title: Optional[str],
) -> str:

    base_text = add_regulation_context_to_text(
        text=text,
        part_name=part_name,
        part_title=part_title,
        paragraph=paragraph,
        paragraph_title=paragraph_title,
    )

    if section_number is not None and section_title:
        section_context = (
            f"Section: "
            f"{section_number}. "
            f"{section_title}"
        )

        return (
            f"{base_text}\n\n"
            f"{section_context}"
        ).strip()

    return base_text


# ============================================================
# MODULE TEXT
# ============================================================

def build_module_text(
    module_code: Optional[str],
    module_name: Optional[str],
    section_title: Optional[str],
    description: Dict[str, Any],
) -> str:

    parts: List[str] = []

    # --------------------------------------------------------
    # Module identity
    # --------------------------------------------------------

    if module_name and module_code:
        parts.append(
            f"Module: {module_name} "
            f"({module_code})"
        )

    elif module_name:
        parts.append(
            f"Module: {module_name}"
        )

    elif module_code:
        parts.append(
            f"Module Code: {module_code}"
        )

    # --------------------------------------------------------
    # Module category
    # --------------------------------------------------------

    if section_title:
        parts.append(
            f"Module Category: {section_title}"
        )

    # --------------------------------------------------------
    # Description fields
    # --------------------------------------------------------

    fields = [
        (
            "Content",
            "content",
        ),
        (
            "Qualification Goals",
            "qualification_goals",
        ),
        (
            "Teaching Forms",
            "teaching_forms",
        ),
        (
            "Prerequisites",
            "prerequisites",
        ),
        (
            "Applicability",
            "applicability",
        ),
        (
            "Credit Requirements",
            "credit_requirements",
        ),
        (
            "Examination",
            "examination",
        ),
        (
            "Credits and Grades",
            "credits_and_grades",
        ),
        (
            "Frequency",
            "frequency",
        ),
        (
            "Workload",
            "workload",
        ),
        (
            "Duration",
            "duration",
        ),
    ]

    for label, key in fields:

        value = description.get(key)

        if value is None:
            continue

        if not isinstance(value, str):
            value = str(value)

        value = clean_chunk_text(value)

        if not value:
            continue

        parts.append(
            f"{label}:\n{value}"
        )

    return "\n\n".join(parts).strip()


# ============================================================
# MAIN CHUNKER
# ============================================================

def chunk_regulation(
    regulation: Dict[str, Any],
) -> List[Chunk]:
    """
    Convert the structured regulation JSON into canonical
    RAG Chunk objects.

    Chunk types:

        regulation
        module_section
        module_description

    The chunker preserves:

        Part
        Paragraph
        Section
        Module

    hierarchy through the `context` field.

    Module-specific metadata is ONLY attached to
    module_description chunks.
    """

    chunks: List[Chunk] = []

    chunk_index = 0

    # --------------------------------------------------------
    # Document ID
    # --------------------------------------------------------

    document_id = regulation.get(
        "document_id",
        "tu_chemnitz_web_engineering_2025",
    )

    # ========================================================
    # PARTS
    # ========================================================

    for part in regulation.get(
        "parts",
        [],
    ):

        part_name = part.get("part")
        part_title = part.get("title")

        # ====================================================
        # REGULATIONS / PARAGRAPHS
        # ====================================================

        for regulation_section in part.get(
            "regulations",
            [],
        ):

            paragraph = regulation_section.get(
                "paragraph"
            )

            paragraph_title = regulation_section.get(
                "title"
            )

            # ==================================================
            # NORMAL REGULATION BLOCKS
            # ==================================================

            for block in regulation_section.get(
                "blocks",
                [],
            ):

                raw_text = block.get("text")

                if not raw_text:
                    continue

                # Remove footer artifacts
                if is_footer_or_artifact(
                    raw_text
                ):
                    continue

                # Remove pure Part transition blocks
                if is_part_transition(
                    raw_text
                ):
                    continue

                text = clean_chunk_text(
                    raw_text
                )

                if not text:
                    continue

                # ----------------------------------------------
                # Context
                # ----------------------------------------------

                context = build_regulation_context(
                    part_name=part_name,
                    part_title=part_title,
                    paragraph=paragraph,
                    paragraph_title=paragraph_title,
                )

                # ----------------------------------------------
                # Context-aware text
                # ----------------------------------------------

                text = add_regulation_context_to_text(
                    text=text,
                    part_name=part_name,
                    part_title=part_title,
                    paragraph=paragraph,
                    paragraph_title=paragraph_title,
                )

                # ----------------------------------------------
                # Create Chunk
                # ----------------------------------------------

                chunk = Chunk(
                    chunk_id=(
                        f"regulation_"
                        f"{chunk_index:05d}"
                    ),

                    chunk_index=chunk_index,

                    document_id=document_id,

                    chunk_type="regulation",

                    text=text,

                    context=context,

                    page_start=block.get(
                        "page_number"
                    ),

                    page_end=block.get(
                        "page_number"
                    ),

                    zone=block.get(
                        "zone"
                    ),

                    block_index=block.get(
                        "block_index"
                    ),
                )

                chunks.append(chunk)

                chunk_index += 1

            # ==================================================
            # MODULE SECTIONS
            # ==================================================

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

                # ==================================================
                # MODULE SECTION BLOCKS
                # ==================================================

                for block in module_section.get(
                    "blocks",
                    [],
                ):

                    raw_text = block.get("text")

                    if not raw_text:
                        continue

                    if is_footer_or_artifact(
                        raw_text
                    ):
                        continue

                    if is_part_transition(
                        raw_text
                    ):
                        continue

                    text = clean_chunk_text(
                        raw_text
                    )

                    if not text:
                        continue

                    # ------------------------------------------
                    # Context
                    # ------------------------------------------

                    context = build_section_context(
                        part_name=part_name,
                        part_title=part_title,
                        paragraph=paragraph,
                        paragraph_title=paragraph_title,
                        section_number=section_number,
                        section_title=section_title,
                    )

                    # ------------------------------------------
                    # Context-aware text
                    # ------------------------------------------

                    text = add_section_context_to_text(
                        text=text,
                        part_name=part_name,
                        part_title=part_title,
                        paragraph=paragraph,
                        paragraph_title=paragraph_title,
                        section_number=section_number,
                        section_title=section_title,
                    )

                    # ------------------------------------------
                    # Create Chunk
                    # ------------------------------------------

                    chunk = Chunk(
                        chunk_id=(
                            f"regulation_"
                            f"{chunk_index:05d}"
                        ),

                        chunk_index=chunk_index,

                        document_id=document_id,

                        chunk_type="module_section",

                        text=text,

                        context=context,

                        page_start=block.get(
                            "page_number"
                        ),

                        page_end=block.get(
                            "page_number"
                        ),

                        zone=block.get(
                            "zone"
                        ),

                        block_index=block.get(
                            "block_index"
                        ),
                    )

                    chunks.append(chunk)

                    chunk_index += 1

                # ==================================================
                # MODULE DESCRIPTIONS
                # ==================================================

                for module in module_section.get(
                    "modules",
                    [],
                ):

                    module_code = module.get(
                        "module_code"
                    )

                    module_name = module.get(
                        "module_name"
                    )

                    module_type = module.get(
                        "type"
                    )

                    credits = module.get(
                        "credits"
                    )

                    description = module.get(
                        "description",
                        {}
                    )

                    if not description:
                        continue

                    # ----------------------------------------------
                    # Module source / provenance
                    # ----------------------------------------------

                    sources = module.get(
                        "sources",
                        {}
                    )

                    module_source = sources.get(
                        "module_description",
                        {}
                    )

                    # ----------------------------------------------
                    # Build module text
                    # ----------------------------------------------

                    module_text = build_module_text(
                        module_code=module_code,
                        module_name=module_name,
                        section_title=section_title,
                        description=description,
                    )

                    if not module_text:
                        continue

                    # ----------------------------------------------
                    # Module context
                    # ----------------------------------------------

                    context = build_module_context(
                        part_name=part_name,
                        part_title=part_title,
                        paragraph=paragraph,
                        paragraph_title=paragraph_title,
                        section_number=section_number,
                        section_title=section_title,
                        module_code=module_code,
                        module_name=module_name,
                        module_type=module_type,
                        credits=credits,
                    )

                    # ----------------------------------------------
                    # Create module chunk
                    # ----------------------------------------------

                    chunk = Chunk(
                        chunk_id=(
                            f"module_"
                            f"{module_code}"
                        ),

                        chunk_index=chunk_index,

                        document_id=document_id,

                        chunk_type="module_description",

                        text=module_text,

                        context=context,

                        page_start=module_source.get(
                            "start_page"
                        ),

                        page_end=module_source.get(
                            "end_page"
                        ),

                        zone=module_source.get(
                            "zone"
                        ),
                    )

                    chunks.append(chunk)

                    chunk_index += 1

    return chunks