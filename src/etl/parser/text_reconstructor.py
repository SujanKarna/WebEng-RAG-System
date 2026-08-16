"""
Text Reconstructor
==================

Reconstructs PDF-extracted text after the cleaning stage.

Responsibilities:
    - Repair words broken by PDF line wrapping.
    - Join normal line breaks.
    - Preserve paragraph boundaries such as (1), (2), etc.
    - Reconstruct text inside cleaned blocks.
    - Keep block metadata unchanged.

This module does NOT:
    - Detect document structure.
    - Detect headings.
    - Detect sections.
    - Classify content.
    - Handle study-plan tables.

Pipeline position:

    Extractor
        ↓
    Zone Detector
        ↓
    Cleaner
        ↓
    Text Reconstructor
        ↓
    Structure Analyzer
        ↓
    Chunker
"""

import re
from copy import deepcopy
from typing import List, Dict, Any


# =============================================================================
# REGEX PATTERNS
# =============================================================================

# Paragraph markers used in German regulations:
#
#     (1)
#     (2)
#     (3)
#     ...
#
PARAGRAPH_MARKER_PATTERN = re.compile(
    r"^\s*\(\d+\)\s+"
)


# Detects a word that has been split by a line-ending hyphen.
#
# Example:
#
#     Enginee-
#     ring
#
# becomes:
#
#     Engineering
#
HYPHENATED_LINE_PATTERN = re.compile(
    r"([A-Za-zÄÖÜäöüß])-\s*$"
)


# Multiple spaces/tabs.
MULTIPLE_SPACES_PATTERN = re.compile(
    r"[ \t]+"
)


# =============================================================================
# BASIC HELPERS
# =============================================================================

def is_paragraph_marker(line: str) -> bool:
    """
    Return True if the line starts with a numbered paragraph marker.

    Example:
        "(1) Ein Studienbeginn ..."
    """

    return bool(PARAGRAPH_MARKER_PATTERN.match(line))


def normalize_line(line: str) -> str:
    """
    Normalize whitespace in a single line.

    We intentionally preserve:
        - punctuation
        - paragraph markers
        - special characters
    """

    line = line.strip()

    if not line:
        return ""

    line = MULTIPLE_SPACES_PATTERN.sub(" ", line)

    return line


# =============================================================================
# LINE RECONSTRUCTION
# =============================================================================

def join_lines(lines: List[str]) -> str:
    """
    Join PDF-wrapped lines.

    Hyphenated words are reconstructed by removing only the
    line-ending hyphen.

    Example:

        Enginee-
        ring

    becomes:

        Engineering
    """

    if not lines:
        return ""

    result = ""

    for raw_line in lines:

        line = normalize_line(raw_line)

        if not line:
            continue

        # First line.
        if not result:
            result = line
            continue

        # -------------------------------------------------------------
        # Check whether previous line ends with a hyphen.
        # -------------------------------------------------------------

        if result.endswith("-"):

            # Remove ONLY the final hyphen.
            result = result[:-1]

            # Directly concatenate the next line.
            result += line

        else:

            # Normal PDF line wrapping.
            result += " " + line

    return result.strip()


# =============================================================================
# TEXT RECONSTRUCTION
# =============================================================================

def is_bullet(line: str) -> bool:
    """
    Check whether a line starts with a bullet.

    Examples:
        • Vorlesung
        • Seminar
        • Projekt
    """

    return bool(re.match(r"^\s*[•●▪◦]\s+", line))


def is_section_marker(line: str) -> bool:
    """
    Check whether a line is a section marker.

    Examples:
        § 1
        § 2
        § 10
    """

    return bool(re.match(r"^\s*§\s*\d+", line))


def reconstruct_text(text: str) -> str:
    """
    Reconstruct extracted PDF text while preserving semantic structure.

    Rules
    -----

    1. Normal line breaks are joined.

    2. Hyphenated words are repaired.

    3. Numbered paragraphs start a new paragraph.

    4. Section markers are kept with their following heading.

    5. Bullets remain separate lines.

    Example:

        Lehrformen:
        • Vorlesung
        • Seminar
        • Übung

    becomes:

        Lehrformen:
        • Vorlesung
        • Seminar
        • Übung
    """

    if not text:
        return ""

    # -----------------------------------------------------------------
    # Normalize newline representation.
    # -----------------------------------------------------------------

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    raw_lines = text.split("\n")

    lines = []

    for raw_line in raw_lines:

        line = normalize_line(raw_line)

        if line:
            lines.append(line)

    if not lines:
        return ""

    paragraphs = []

    current_lines = []

    i = 0

    while i < len(lines):

        line = lines[i]

        # =============================================================
        # SECTION MARKER
        # =============================================================
        #
        # Example:
        #
        #     § 3
        #     Zugangsvoraussetzungen
        #
        # We combine the marker with the following heading.
        #

        if is_section_marker(line):

            # Finish anything before the section marker.
            if current_lines:

                paragraph = join_lines(current_lines)

                if paragraph:
                    paragraphs.append(paragraph)

                current_lines = []

            # If the next line exists, combine it with § 3.
            if i + 1 < len(lines):

                next_line = lines[i + 1]

                # Do not combine if the next line starts a paragraph
                # or bullet.
                if (
                    not is_paragraph_marker(next_line)
                    and not is_bullet(next_line)
                    and not is_section_marker(next_line)
                ):

                    paragraphs.append(
                        line + " " + next_line
                    )

                    i += 2
                    continue

            paragraphs.append(line)

            i += 1
            continue

        # =============================================================
        # PARAGRAPH MARKER
        # =============================================================

        if is_paragraph_marker(line):

            # Finish previous paragraph.
            if current_lines:

                paragraph = join_lines(current_lines)

                if paragraph:
                    paragraphs.append(paragraph)

            # Start new paragraph.
            current_lines = [line]

            i += 1
            continue

        # =============================================================
        # BULLET
        # =============================================================

        if is_bullet(line):

            # Finish normal text before the bullet.
            if current_lines:

                paragraph = join_lines(current_lines)

                if paragraph:
                    paragraphs.append(paragraph)

                current_lines = []

            # Add bullet as its own semantic line.
            paragraphs.append(line)

            i += 1
            continue

        # =============================================================
        # NORMAL TEXT
        # =============================================================

        current_lines.append(line)

        i += 1

    # -----------------------------------------------------------------
    # Final paragraph.
    # -----------------------------------------------------------------

    if current_lines:

        paragraph = join_lines(current_lines)

        if paragraph:
            paragraphs.append(paragraph)

    return "\n".join(paragraphs)

# =============================================================================
# BLOCK RECONSTRUCTION
# =============================================================================

def reconstruct_block(block: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconstruct the text of one cleaned block.

    The original block is NOT modified.

    A deep copy is returned so that the previous pipeline stage
    remains reproducible.

    Expected block structure:

        {
            "page_index": 1,
            "page_number": 2,
            "block_index": 4,
            "zone": "main_regulations",
            "text": "..."
        }

    Returns:

        reconstructed copy of the block
    """

    reconstructed = deepcopy(block)

    text = reconstructed.get("text", "")

    reconstructed["text"] = reconstruct_text(text)

    return reconstructed


# =============================================================================
# BLOCK LIST RECONSTRUCTION
# =============================================================================

def reconstruct_blocks(
    blocks: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Reconstruct all cleaned blocks.

    Args:
        blocks:
            List of cleaned PDF blocks.

    Returns:
        List of reconstructed blocks.

    Important:
        Block order and metadata are preserved.
    """

    reconstructed_blocks = []

    for block in blocks:

        reconstructed = reconstruct_block(block)

        # Don't keep completely empty blocks.
        if reconstructed.get("text", "").strip():

            reconstructed_blocks.append(reconstructed)

    return reconstructed_blocks