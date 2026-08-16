"""
Document Cleaner
================

Cleans zone-annotated PDF extraction blocks.

Responsibilities
----------------
1. Remove unwanted document zones.
2. Remove publication headers and footers.
3. Normalize extracted text.
4. Remove empty blocks.
5. Preserve useful provenance metadata.

The cleaner does NOT:
- detect sections
- detect headings
- chunk text
- generate embeddings

Those are separate pipeline stages.
"""

from dataclasses import dataclass, asdict
from typing import Any
import re

from src.etl.parser.zone_detector import DocumentZone
from src.etl.parser.toc.toc_processor import process_toc

# ============================================================
# CLEAN BLOCK
# ============================================================

@dataclass
class CleanBlock:
    """
    Represents a cleaned piece of document content.

    This is intentionally much smaller than the raw PDF block.

    Raw extraction details such as individual spans and font
    information are no longer needed after cleaning.
    """

    # --------------------------------------------------------
    # Source identification
    # --------------------------------------------------------

    page_index: int

    page_number: int

    block_index: int

    # --------------------------------------------------------
    # Document location
    # --------------------------------------------------------

    bbox: list[float]

    # --------------------------------------------------------
    # Structural information
    # --------------------------------------------------------

    zone: str

    # --------------------------------------------------------
    # Cleaned textual content
    # --------------------------------------------------------

    text: str

    # --------------------------------------------------------
    # Original block reference
    # --------------------------------------------------------

    source_block_index: int


# ============================================================
# CONFIGURATION
# ============================================================

# Zones that should NOT enter the RAG knowledge base.

EXCLUDED_ZONES = {
    DocumentZone.INTRODUCTION.value,
    DocumentZone.TABLE_OF_CONTENTS.value,
    DocumentZone.STUDY_PLAN.value,
}


# Zones that contain actual knowledge.

RETAINED_ZONES = {
    DocumentZone.MAIN_REGULATIONS.value,
    DocumentZone.MODULE_DESCRIPTIONS.value,
}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_block_text(
    block: dict[str, Any],
) -> str:
    """
    Reconstruct text from the raw extraction block.

    The extractor stores text as:

        block
            └── lines
                  └── spans
                        └── text

    We reconstruct the text while preserving line boundaries.
    """

    lines = []

    for line in block.get("lines", []):

        spans = line.get(
            "spans",
            [],
        )

        line_text = "".join(
            span.get("text", "")
            for span in spans
        )

        if line_text.strip():

            lines.append(
                line_text.strip()
            )

    return "\n".join(lines)


# ============================================================
# WHITESPACE NORMALIZATION
# ============================================================

def normalize_whitespace(
    text: str,
) -> str:
    """
    Normalize whitespace without destroying paragraph
    structure.

    Examples
    --------

    Multiple spaces:

        "hello    world"

    becomes:

        "hello world"


    Excessive blank lines:

        "hello\\n\\n\\nworld"

    becomes:

        "hello\\n\\nworld"
    """

    # --------------------------------------------------------
    # Normalize spaces/tabs inside lines.
    # --------------------------------------------------------

    lines = []

    for line in text.splitlines():

        line = re.sub(
            r"[ \t]+",
            " ",
            line,
        )

        line = line.strip()

        if line:
            lines.append(line)

    # --------------------------------------------------------
    # Preserve one newline between meaningful lines.
    # --------------------------------------------------------

    return "\n".join(lines)


# ============================================================
# HYPHENATION CLEANING
# ============================================================

def repair_line_break_hyphenation(
    text: str,
) -> str:
    """
    Repair words broken across PDF line boundaries.

    Example:

        konsekuti-
        ven

    becomes:

        konsekutiven

    This only handles a hyphen immediately followed by a
    lowercase continuation on the next line.

    We deliberately do NOT remove normal hyphens inside words.

    Example:

        Teilzeitstudium
        Web-Engineering

    should remain unchanged.
    """

    text = re.sub(
        r"(?<=[A-Za-zÄÖÜäöüß])-\n(?=[a-zäöüß])",
        "",
        text,
    )

    return text


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(
    text: str,
) -> str:
    """
    Apply all textual cleaning operations.
    """

    # --------------------------------------------------------
    # Repair words split across lines.
    # --------------------------------------------------------

    text = repair_line_break_hyphenation(
        text
    )

    # --------------------------------------------------------
    # Normalize whitespace.
    # --------------------------------------------------------

    text = normalize_whitespace(
        text
    )

    return text.strip()


# ============================================================
# PUBLICATION HEADER / FOOTER DETECTION
# ============================================================

def is_publication_header_or_footer(
    text: str,
) -> bool:
    """
    Detect recurring official-publication header/footer text.

    These elements are not part of the actual study regulation
    content and should not be embedded.

    IMPORTANT:
    This function should remain conservative.

    We do not remove arbitrary short text because short text
    may be legitimate headings such as:

        § 1 Geltungsbereich
    """

    normalized = " ".join(
        text.split()
    ).lower()

    # --------------------------------------------------------
    # Official publication header.
    # --------------------------------------------------------

    if normalized == "amtliche bekanntmachungen":
        return True

    # --------------------------------------------------------
    # Official publication footer/header.
    # --------------------------------------------------------

    if (
        normalized.startswith(
            "amtliche bekanntmachungen"
        )
        and "nr. 48/2025" in normalized
    ):
        return True

    # --------------------------------------------------------
    # Publication number.
    # --------------------------------------------------------

    if re.fullmatch(
        r"nr\.?\s*48/2025",
        normalized,
    ):
        return True

    # --------------------------------------------------------
    # Publication date.
    # --------------------------------------------------------

    if normalized in {
        "19. dezember 2025",
        "vom 19. dezember 2025",
    }:
        return True

    # --------------------------------------------------------
    # Page numbers printed by the publication.
    #
    # We deliberately keep this conservative because actual
    # regulation content can contain numbers.
    # --------------------------------------------------------

    if re.fullmatch(
        r"seite\s+\d+",
        normalized,
    ):
        return True

    return False


# ============================================================
# BLOCK CLEANING
# ============================================================

def clean_block(
    block: dict[str, Any],
    page: dict[str, Any],
) -> CleanBlock | None:
    """
    Clean a single extracted block.

    Returns
    -------
    CleanBlock
        If the block should be retained.

    None
        If the block should be discarded.
    """

    # --------------------------------------------------------
    # Get zone.
    # --------------------------------------------------------

    zone = block.get(
        "zone"
    )

    # --------------------------------------------------------
    # Safety check.
    #
    # The cleaner expects zone detection to have already run.
    # --------------------------------------------------------

    if zone is None:

        raise ValueError(
            "Block does not contain a 'zone'. "
            "Run zone detection before cleaning."
        )

    # --------------------------------------------------------
    # Remove unwanted zones.
    # --------------------------------------------------------

    if zone in EXCLUDED_ZONES:

        return None

    # --------------------------------------------------------
    # Only retain knowledge-bearing zones.
    # --------------------------------------------------------

    if zone not in RETAINED_ZONES:

        return None

    # --------------------------------------------------------
    # Extract raw text.
    # --------------------------------------------------------

    raw_text = extract_block_text(
        block
    )

    # --------------------------------------------------------
    # Clean text.
    # --------------------------------------------------------

    text = clean_text(
        raw_text
    )

    # --------------------------------------------------------
    # Remove empty blocks.
    # --------------------------------------------------------

    if not text:

        return None

    # --------------------------------------------------------
    # Remove publication headers and footers.
    # --------------------------------------------------------

    if is_publication_header_or_footer(
        text
    ):

        return None

    # --------------------------------------------------------
    # Page metadata.
    # --------------------------------------------------------

    page_index = page.get(
        "page_index",
        0,
    )

    page_number = page.get(
        "page_number",
        page_index + 1,
    )

    # --------------------------------------------------------
    # Bounding box.
    # --------------------------------------------------------

    bbox = block.get(
        "bbox",
        [],
    )

    # --------------------------------------------------------
    # Block index.
    # --------------------------------------------------------

    block_index = block.get(
        "block_index",
        -1,
    )

    # --------------------------------------------------------
    # Construct clean block.
    # --------------------------------------------------------

    return CleanBlock(
        page_index=page_index,
        page_number=page_number,
        block_index=block_index,
        bbox=bbox,
        zone=zone,
        text=text,
        source_block_index=block_index,
    )


# ============================================================
# DOCUMENT CLEANING
# ============================================================

def clean(
    pages: list[dict[str, Any]],
) -> list[CleanBlock]:
    """
    Clean the entire zone-annotated document.

    Parameters
    ----------
    pages:
        Extracted pages whose blocks already contain a
        "zone" field.

    Returns
    -------
    list[CleanBlock]
        Cleaned blocks.
    """

    cleaned_blocks: list[CleanBlock] = []

    # --------------------------------------------------------
    # Process pages in document order.
    # --------------------------------------------------------

    for page in pages:

        # ----------------------------------------------------
        # Process blocks in extraction order.
        # ----------------------------------------------------

        for block in page.get(
            "blocks",
            [],
        ):

            cleaned = clean_block(
                block=block,
                page=page,
            )

            # ------------------------------------------------
            # Keep only blocks that survived cleaning.
            # ------------------------------------------------

            if cleaned is not None:

                cleaned_blocks.append(
                    cleaned
                )

    return cleaned_blocks


# ============================================================
# SERIALIZATION HELPER
# ============================================================

def clean_blocks_to_dicts(
    blocks: list[CleanBlock],
) -> list[dict[str, Any]]:
    """
    Convert CleanBlock dataclasses into dictionaries.

    Useful when saving the cleaned result to JSON.
    """

    return [
        asdict(block)
        for block in blocks
    ]