from typing import Any


# ============================================================
# TEXT EXTRACTION
# ============================================================

def get_block_text(
    block: dict[str, Any],
) -> str:
    """
    Reconstruct the text of a raw extracted block.

    Raw extraction structure:

        block
            └── lines
                 └── spans
                      └── text
    """

    parts: list[str] = []

    for line in block.get("lines", []):

        line_parts: list[str] = []

        for span in line.get("spans", []):

            text = span.get("text", "")

            if text:
                line_parts.append(text)

        line_text = "".join(line_parts).strip()

        if line_text:
            parts.append(line_text)

    return "\n".join(parts)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    Basic text normalization.

    Keeps paragraph/newline structure intact.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)


# ============================================================
# SINGLE BLOCK CLEANING
# ============================================================

def clean_block(
    block: dict[str, Any],
    page: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Clean a single raw block.

    The page is supplied separately because page_number
    belongs to the page-level extraction structure.
    """

    zone = block.get("zone")

    # --------------------------------------------------------
    # Only keep zones currently required
    # --------------------------------------------------------

    if zone not in {
        "main_regulations",
        "module_descriptions",
    }:
        return None

    # --------------------------------------------------------
    # Reconstruct text from spans
    # --------------------------------------------------------

    text = get_block_text(block)

    if not text:
        return None

    text = normalize_text(text)

    if not text:
        return None

    # --------------------------------------------------------
    # Preserve provenance
    # --------------------------------------------------------

    return {
        "block_index": block.get("block_index"),
        "page_index": page.get("page_index"),
        "page_number": page.get("page_number"),
        "zone": zone,
        "text": text,
    }


# ============================================================
# DOCUMENT CLEANING
# ============================================================

def clean_blocks(
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Clean all relevant blocks in the document.

    Only:

        main_regulations
        module_descriptions

    are retained.
    """

    cleaned_blocks: list[dict[str, Any]] = []

    for page in pages:

        for block in page.get("blocks", []):

            cleaned = clean_block(
                block,
                page,
            )

            if cleaned is None:
                continue

            cleaned_blocks.append(
                cleaned
            )

    return cleaned_blocks