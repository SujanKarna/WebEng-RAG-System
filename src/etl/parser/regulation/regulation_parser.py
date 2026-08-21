"""
Regulation Parser
=================

Builds the hierarchical structure of the main study regulation.

Input
-----

1. Cleaned blocks
2. Structured TOC

Output
------

Teil
    └── §
         ├── blocks
         └── sections       # §6 only
              └── modules

The parser preserves and enriches the original cleaned block
objects instead of creating new block dictionaries.
"""

import re
from typing import Any

from src.etl.parser.regulation.section6_parser import (
    parse_section_6,
)


# ============================================================
# CONSTANTS
# ============================================================

MAIN_REGULATION_ZONE = "main_regulations"


# ============================================================
# REGEX
# ============================================================

PART_PATTERN = re.compile(
    r"^\s*(Teil\s+\d+)\s*:?\s*(.*?)\s*$",
    re.IGNORECASE,
)

PARAGRAPH_PATTERN = re.compile(
    r"^\s*(§\s*\d+)\s*(.*?)\s*$"
)

PARAGRAPH_NUMBER_PATTERN = re.compile(
    r"^(§\s*\d+)\b"
)


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    Normalize whitespace while preserving the actual words.
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


# ============================================================
# PART / PARAGRAPH DETECTION
# ============================================================

def parse_part_heading(
    text: str,
) -> tuple[str, str] | None:
    """
    Parse:

        Teil 1 Allgemeine Bestimmungen

    Returns:

        ("Teil 1", "Allgemeine Bestimmungen")
    """

    text = normalize_text(text)

    match = PART_PATTERN.match(text)

    if not match:
        return None

    return (
        match.group(1),
        match.group(2).strip(),
    )


def parse_paragraph_heading(
    text: str,
) -> tuple[str, str] | None:
    """
    Parse:

        § 5 Ziele des Studienganges

    Returns:

        ("§ 5", "Ziele des Studienganges")
    """

    text = normalize_text(text)

    match = PARAGRAPH_PATTERN.match(text)

    if not match:
        return None

    return (
        match.group(1),
        match.group(2).strip(),
    )


# ============================================================
# TOC INDEX
# ============================================================

def build_toc_index(
    toc: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """
    Convert the structured TOC into a lookup index.

    Example:

        {
            "§ 1": {
                "part": "Teil 1",
                "part_title": "Allgemeine Bestimmungen",
                "paragraph": "§ 1",
                "title": "Geltungsbereich"
            }
        }
    """

    index: dict[str, dict[str, Any]] = {}

    for part in toc.get("parts", []):

        part_name = part.get(
            "part",
            "",
        )

        part_title = part.get(
            "title",
            "",
        )

        for regulation in part.get(
            "regulations",
            [],
        ):

            paragraph = regulation.get(
                "paragraph",
                "",
            )

            if not paragraph:
                continue

            index[paragraph] = {
                "part": part_name,
                "part_title": part_title,
                "paragraph": paragraph,
                "title": regulation.get(
                    "title",
                    "",
                ),
            }

    return index


# ============================================================
# FIND PARAGRAPH
# ============================================================

def find_paragraph_number(
    text: str,
) -> str | None:
    """
    Find a paragraph marker at the beginning of a block.

    Examples:

        § 1 Geltungsbereich

        § 5 Ziele des Studienganges

    Returns:

        § 1

        § 5
    """

    text = normalize_text(text)

    match = PARAGRAPH_NUMBER_PATTERN.match(
        text
    )

    if not match:
        return None

    return normalize_text(
        match.group(1)
    )


# ============================================================
# PARAGRAPH TEXT
# ============================================================

def remove_paragraph_heading(
    text: str,
) -> str:
    """
    Remove the § heading from the beginning of a block.

    Example:

        § 1 Geltungsbereich
        Diese Studienordnung ...

    becomes:

        Diese Studienordnung ...
    """

    text = text.strip()

    match = re.match(
        r"^§\s*\d+\s+[^\n]+",
        text,
    )

    if not match:
        return text

    remainder = text[
        match.end():
    ]

    return remainder.strip()


# ============================================================
# CREATE PART STRUCTURE
# ============================================================

def create_part(
    part: dict[str, Any],
) -> dict[str, Any]:
    """
    Create the Part structure.
    """

    return {
        "part": part.get(
            "part",
            "",
        ),
        "title": part.get(
            "title",
            "",
        ),
        "regulations": [],
    }


# ============================================================
# CREATE REGULATION STRUCTURE
# ============================================================

def create_regulation(
    regulation: dict[str, Any],
) -> dict[str, Any]:
    """
    Create the regulation structure.

    Every regulation keeps its original blocks.

    §6 additionally receives:

        "sections": []
    """

    result = {
        "paragraph": regulation.get(
            "paragraph",
            "",
        ),
        "title": regulation.get(
            "title",
            "",
        ),
        "blocks": [],
    }

    # --------------------------------------------------------
    # §6 will later contain:
    #
    # sections
    #   ├── category
    #   └── modules
    # --------------------------------------------------------

    if regulation.get(
        "paragraph"
    ) == "§ 6":

        result["sections"] = []

    return result


# ============================================================
# ANNOTATE BLOCK
# ============================================================

def annotate_block(
    block: dict[str, Any],
    part: dict[str, Any],
    regulation: dict[str, Any],
) -> dict[str, Any]:
    """
    Enrich the ORIGINAL cleaned block.

    No copy is created.

    Existing metadata such as:

        block_index
        page_index
        page_number
        zone
        text

    is preserved.

    Additional hierarchy metadata is added:

        part
        part_title
        paragraph
        paragraph_title
    """

    block["part"] = part["part"]

    block["part_title"] = part["title"]

    block["paragraph"] = (
        regulation["paragraph"]
    )

    block["paragraph_title"] = (
        regulation["title"]
    )

    return block


# ============================================================
# PARSE REGULATIONS
# ============================================================

def parse_regulations(
    blocks: list[dict[str, Any]],
    toc: dict[str, Any],
) -> dict[str, Any]:
    """
    Assign cleaned main-regulation blocks to the correct
    Teil and § using the TOC.

    The original cleaned block objects are preserved and
    enriched with hierarchy metadata.
    """

    # ========================================================
    # CREATE OUTPUT STRUCTURE FROM TOC
    # ========================================================

    result: dict[str, Any] = {
        "parts": []
    }

    for part in toc.get(
        "parts",
        [],
    ):

        part_structure = create_part(
            part
        )

        result["parts"].append(
            part_structure
        )

        for regulation in part.get(
            "regulations",
            [],
        ):

            part_structure["regulations"].append(
                create_regulation(
                    regulation
                )
            )

    # ========================================================
    # REGULATION LOOKUP
    # ========================================================

    regulation_lookup: dict[
        str,
        tuple[
            dict[str, Any],
            dict[str, Any],
        ],
    ] = {}

    for part in result["parts"]:

        for regulation in part[
            "regulations"
        ]:

            regulation_lookup[
                regulation["paragraph"]
            ] = (
                part,
                regulation,
            )

    # ========================================================
    # CURRENT LOCATION
    # ========================================================

    current_part: dict[str, Any] | None = None

    current_regulation: dict[
        str,
        Any,
    ] | None = None

    # ========================================================
    # PROCESS BLOCKS IN DOCUMENT ORDER
    # ========================================================

    for block in blocks:

        # ----------------------------------------------------
        # Only main regulation
        # ----------------------------------------------------

        if block.get(
            "zone"
        ) != MAIN_REGULATION_ZONE:

            continue

        text = block.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        # ----------------------------------------------------
        # Detect paragraph heading
        # ----------------------------------------------------

        paragraph_number = find_paragraph_number(
            text
        )

        if paragraph_number:

            location = regulation_lookup.get(
                paragraph_number
            )

            if location is not None:

                (
                    current_part,
                    current_regulation,
                ) = location

        # ----------------------------------------------------
        # Ignore blocks before first known paragraph
        # ----------------------------------------------------

        if (
            current_part is None
            or current_regulation is None
        ):
            continue

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Enrich the ORIGINAL block.
        #
        # We do NOT create:
        #
        #     new_block = {...}
        #
        # The same object from cleaned_blocks is used.
        # ----------------------------------------------------

        annotate_block(
            block=block,
            part=current_part,
            regulation=current_regulation,
        )

        # ----------------------------------------------------
        # Store the SAME block object
        # ----------------------------------------------------

        current_regulation[
            "blocks"
        ].append(
            block
        )

    # ========================================================
    # §6 SPECIAL STRUCTURE
    # ========================================================

    for part in result["parts"]:

        for regulation in part[
            "regulations"
        ]:

            if regulation[
                "paragraph"
            ] != "§ 6":

                continue

            # ------------------------------------------------
            # Parse §6 using its already-enriched blocks.
            #
            # The section6 parser therefore receives exactly
            # the same block objects that are stored inside
            # regulation["blocks"].
            # ------------------------------------------------

            section_6 = parse_section_6(
                regulation["blocks"]
            )

            regulation[
                "module_sections"
            ] = section_6[
                "sections"
            ]

    # ========================================================
    # Parse § 6 module structure
    # ========================================================

    for part in result["parts"]:

        for regulation in part["regulations"]:

            if regulation["paragraph"] != "§ 6":
                continue

            section_6 = parse_section_6(
                regulation["blocks"]
            )

            regulation["module_sections"] = (
                section_6["sections"]
            )

            regulation["overall_blocks"] = (
                section_6["overall_blocks"]
            )

            break

    return result


# ============================================================
# PUBLIC API
# ============================================================

def structure_regulations(
    blocks: list[dict[str, Any]],
    toc: dict[str, Any],
) -> dict[str, Any]:
    """
    Public entry point.

    Keeps main.py clean.
    """

    return parse_regulations(
        blocks=blocks,
        toc=toc,
    )