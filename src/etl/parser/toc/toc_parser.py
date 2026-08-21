"""
TOC Parser
==========

Converts cleaned/extracted TOC blocks into a structured
navigation hierarchy:

    Teil
      └── §

The parser does not read files and does not save files.
"""

import re
from typing import Any


# ============================================================
# REGEX
# ============================================================

PART_PATTERN = re.compile(
    r"^\s*(Teil\s+\d+)\s*:?\s*(.*?)\s*$",
    re.IGNORECASE,
)

PARAGRAPH_PATTERN = re.compile(
    r"(§\s*\d+)\s+([^§]+?)(?=\s+§\s*\d+|$)"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """Normalize whitespace."""

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


# ============================================================
# PART
# ============================================================

def parse_part(text: str) -> dict[str, Any]:

    text = normalize_text(text)

    match = PART_PATTERN.match(text)

    if not match:
        raise ValueError(
            f"Invalid Teil heading: {text}"
        )

    return {
        "part": match.group(1),
        "title": match.group(2).strip(),
        "regulations": [],
    }


# ============================================================
# PARAGRAPHS
# ============================================================

def parse_paragraphs(text: str) -> list[dict[str, str]]:
    """
    Extract multiple § entries from one TOC block.

    Example:

        § 1 Geltungsbereich
        § 2 Studienbeginn und Regelstudienzeit
        § 3 Zugangsvoraussetzungen

    becomes three regulation entries.
    """

    text = normalize_text(text)

    matches = PARAGRAPH_PATTERN.findall(text)

    regulations = []

    for paragraph, title in matches:

        regulations.append(
            {
                "paragraph": normalize_text(paragraph),
                "title": normalize_text(title),
            }
        )

    return regulations


# ============================================================
# TOC PARSER
# ============================================================

def parse_toc(
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Parse TOC blocks into:

        {
            "parts": [...]
        }

    Only table_of_contents blocks are processed.
    """

    toc = {
        "parts": []
    }

    current_part = None

    for block in blocks:

        if block.get("zone") != "table_of_contents":
            continue

        text = block.get("text", "")

        if not text:
            continue

        text = normalize_text(text)

        # ----------------------------------------------------
        # Ignore heading
        # ----------------------------------------------------

        if text.lower() == "inhaltsübersicht":
            continue

        # ----------------------------------------------------
        # Ignore page number
        # ----------------------------------------------------

        if text.isdigit():
            continue

        # ----------------------------------------------------
        # Ignore Anlagen entry
        # ----------------------------------------------------

        if text.lower().startswith("anlagen:"):
            continue

        # ----------------------------------------------------
        # Detect Teil
        # ----------------------------------------------------

        part_match = PART_PATTERN.match(text)

        if part_match:

            current_part = parse_part(text)

            toc["parts"].append(
                current_part
            )

            continue

        # ----------------------------------------------------
        # Detect § entries
        # ----------------------------------------------------

        if "§" in text:

            if current_part is None:

                raise ValueError(
                    f"Paragraph found before Teil: {text}"
                )

            regulations = parse_paragraphs(text)

            current_part["regulations"].extend(
                regulations
            )

    return toc