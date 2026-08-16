from enum import Enum
from typing import Any


# ============================================================
# DOCUMENT ZONES
# ============================================================

class DocumentZone(str, Enum):
    """
    Major structural zones of the study regulation.
    """

    INTRODUCTION = "introduction"

    TABLE_OF_CONTENTS = "table_of_contents"

    MAIN_REGULATIONS = "main_regulations"

    STUDY_PLAN = "study_plan"

    MODULE_DESCRIPTIONS = "module_descriptions"


# ============================================================
# STRUCTURAL MARKERS
# ============================================================

# ------------------------------------------------------------
# Introduction → Table of Contents
# ------------------------------------------------------------
#
# We intentionally use "Inhaltsübersicht" and NOT
# "Inhaltsverzeichnis".
#
# The PDF contains "Inhaltsverzeichnis" in the official
# publication header, but the actual regulation starts its
# table of contents with "Inhaltsübersicht".
# ------------------------------------------------------------

TOC_MARKER = "Inhaltsübersicht"


# ------------------------------------------------------------
# Table of Contents → Main Regulations
# ------------------------------------------------------------

MAIN_REGULATIONS_MARKER = (
    "Teil 1 Allgemeine Bestimmungen"
)


# ------------------------------------------------------------
# Main Regulations → Study Plan
# ------------------------------------------------------------
#
# Do NOT use:
#
#     "Anlage 1"
#
# because the regulation contains references such as:
#
#     "(siehe Anlage 1)"
#
# Instead we identify the actual heading.
# ------------------------------------------------------------

STUDY_PLAN_MARKER = (
    "Anlage 1: Englischsprachiger konsekutiver Studiengang "
    "Web Engineering mit dem Abschluss Master of Science"
)


# ------------------------------------------------------------
# Study Plan → Module Descriptions
# ------------------------------------------------------------
#
# Again, do NOT use simply "Anlage 2".
# ------------------------------------------------------------

MODULE_DESCRIPTIONS_MARKER = (
    "Anlage 2: Modulbeschreibung zum englischsprachigen "
    "konsekutiven Studiengang Web Engineering"
)


# ============================================================
# TEXT EXTRACTION
# ============================================================

def get_block_text(block: dict[str, Any]) -> str:
    """
    Reconstruct the complete text of an extracted block.

    The extraction JSON stores text inside:

        block
            └── lines
                  └── spans
                        └── text

    Parameters
    ----------
    block:
        Extracted PDF block.

    Returns
    -------
    str
        Normalized block text.
    """

    parts: list[str] = []

    for line in block.get("lines", []):

        line_parts = []

        for span in line.get("spans", []):

            text = span.get("text", "")

            if text:
                line_parts.append(text)

        line_text = "".join(line_parts).strip()

        if line_text:
            parts.append(line_text)

    return " ".join(parts)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text before marker comparison.

    This handles:

    - leading/trailing whitespace
    - repeated whitespace
    - newlines
    - tabs

    We intentionally do NOT remove punctuation because
    punctuation helps us distinguish structural headings
    from ordinary references.
    """

    return " ".join(text.split())


# ============================================================
# MARKER DETECTION
# ============================================================

def is_toc_marker(text: str) -> bool:
    """
    Check whether a block marks the beginning of the
    actual table of contents.
    """

    return TOC_MARKER.lower() in text.lower()


def is_main_regulations_marker(text: str) -> bool:
    """
    Check whether a block marks the beginning of the
    main study regulation.
    """

    return MAIN_REGULATIONS_MARKER.lower() in text.lower()


def is_study_plan_marker(text: str) -> bool:
    """
    Check whether a block is the actual Anlage 1 heading.

    This prevents false positives from text such as:

        siehe Anlage 1

        Studienablaufplan (siehe Anlage 1)
    """

    return STUDY_PLAN_MARKER.lower() in text.lower()


def is_module_descriptions_marker(text: str) -> bool:
    """
    Check whether a block is the actual Anlage 2 heading.

    This prevents false positives from text such as:

        siehe Anlage 2

        in den Modulbeschreibungen ...
    """

    return MODULE_DESCRIPTIONS_MARKER.lower() in text.lower()


# ============================================================
# ZONE TRANSITION
# ============================================================

def detect_zone_transition(
    current_zone: DocumentZone,
    block_text: str,
) -> DocumentZone:
    """
    Determine whether the current block causes a zone
    transition.

    The detector behaves like a state machine.

    This is important because the same words can appear
    later inside normal text.

    Example:

        MAIN_REGULATIONS
            ↓
        "siehe Anlage 1"

    must remain MAIN_REGULATIONS.

    Only the valid structural heading can cause the
    transition.
    """

    text = normalize_text(block_text)

    # --------------------------------------------------------
    # INTRODUCTION → TABLE OF CONTENTS
    # --------------------------------------------------------

    if current_zone == DocumentZone.INTRODUCTION:

        if is_toc_marker(text):

            return DocumentZone.TABLE_OF_CONTENTS

        return current_zone

    # --------------------------------------------------------
    # TABLE OF CONTENTS → MAIN REGULATIONS
    # --------------------------------------------------------

    if current_zone == DocumentZone.TABLE_OF_CONTENTS:

        if is_main_regulations_marker(text):

            return DocumentZone.MAIN_REGULATIONS

        return current_zone

    # --------------------------------------------------------
    # MAIN REGULATIONS → STUDY PLAN
    # --------------------------------------------------------

    if current_zone == DocumentZone.MAIN_REGULATIONS:

        if is_study_plan_marker(text):

            return DocumentZone.STUDY_PLAN

        return current_zone

    # --------------------------------------------------------
    # STUDY PLAN → MODULE DESCRIPTIONS
    # --------------------------------------------------------

    if current_zone == DocumentZone.STUDY_PLAN:

        if is_module_descriptions_marker(text):

            return DocumentZone.MODULE_DESCRIPTIONS

        return current_zone

    # --------------------------------------------------------
    # MODULE DESCRIPTIONS
    # --------------------------------------------------------
    #
    # This is the final zone.
    #
    # There are no further transitions.
    # --------------------------------------------------------

    return current_zone


# ============================================================
# DOCUMENT ZONE DETECTION
# ============================================================

def detect_zones(
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Assign a document zone to every extracted block.

    Parameters
    ----------
    pages:
        Extracted PDF pages.

    Returns
    -------
    list
        Pages with every block annotated with:

            "zone": <zone value>

    Example:

        {
            "block_index": 12,
            ...
            "zone": "table_of_contents"
        }
    """

    # --------------------------------------------------------
    # Every document starts in the introduction.
    # --------------------------------------------------------

    current_zone = DocumentZone.INTRODUCTION

    # --------------------------------------------------------
    # Process pages in document order.
    # --------------------------------------------------------

    for page in pages:

        blocks = page.get("blocks", [])

        for block in blocks:

            # ------------------------------------------------
            # Extract block text.
            # ------------------------------------------------

            block_text = get_block_text(block)

            # ------------------------------------------------
            # Check whether this block causes a transition.
            # ------------------------------------------------

            new_zone = detect_zone_transition(
                current_zone=current_zone,
                block_text=block_text,
            )

            # ------------------------------------------------
            # Update current zone.
            # ------------------------------------------------

            current_zone = new_zone

            # ------------------------------------------------
            # Store zone directly on the block.
            #
            # This is important because later stages such as
            # the cleaner, segmenter and chunker can directly
            # access:
            #
            #     block["zone"]
            #
            # without having to run the detector again.
            # ------------------------------------------------

            block["zone"] = current_zone.value

    return pages


# ============================================================
# SINGLE BLOCK UTILITY
# ============================================================

def get_zone_for_block(
    current_zone: DocumentZone,
    block: dict[str, Any],
) -> DocumentZone:
    """
    Convenience function for processing a single block.

    Useful for testing or streaming extraction.
    """

    text = get_block_text(block)

    return detect_zone_transition(
        current_zone=current_zone,
        block_text=text,
    )