"""
Section 6 Parser
================

Parses § 6 "Aufbau des Studiums" into structured module sections.

The parser preserves the original cleaned blocks and their provenance.

Expected structure:

§ 6

├── overall_blocks
│
├── module_sections
│   ├── 1. Grundlagenmodule
│   ├── 2. Vertiefungsmodule
│   ├── 3. Module Schlüsselkompetenzen
│   ├── 4. Modul Forschungsseminar
│   ├── 5. Challengemodule
│   └── 6. Modul Master-Arbeit
│
└── remaining_blocks

Each module keeps:

    module_code
    module_name
    credits
    type

and provenance:

    block_index
    page_index
    page_number
    part
    part_title
    paragraph
    paragraph_title

and source location:

    sources
        └── main_regulation
"""

import re

from typing import Any

from src.etl.models.source import (
    create_source_range,
)


# ============================================================
# REGEX
# ============================================================

MODULE_PATTERN = re.compile(
    r"(?P<code>\d{6}-\d{3})\s+"
    r"(?P<name>.+?),\s*"
    r"(?P<credits>\d+)\s*LP"
    r"\s*\(?\s*(?P<type>[^)]+?)\s*\)?",
    re.IGNORECASE,
)


# Matches:
#
# 1.
#
SECTION_NUMBER_PATTERN = re.compile(
    r"^\s*(\d+)\.\s*$"
)


# Matches:
#
# 1. Grundlagenmodule:
# 4. Modul Forschungsseminar:
#
SECTION_INLINE_PATTERN = re.compile(
    r"^\s*(\d+)\.\s+(.+?)\s*:?\s*$"
)


# Matches:
#
# 1.
#
# We intentionally search line-by-line.
SECTION_NUMBER_ONLY_PATTERN = re.compile(
    r"^\s*(\d+)\.\s*$"
)


# Matches § 6 at the beginning of a block.
PARAGRAPH_PATTERN = re.compile(
    r"^\s*§\s*6\b"
)


# Matches paragraph (2), (3), etc.
PARAGRAPH_CONTENT_PATTERN = re.compile(
    r"^\s*\(?(\d+)\)"
)


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    Normalize whitespace while preserving words.
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def clean_section_title(
    title: str,
) -> str:
    """
    Normalize a section title.

    Example:

        Grundlagenmodule:

    becomes:

        Grundlagenmodule
    """

    title = normalize_text(title)

    if title.endswith(":"):
        title = title[:-1].strip()

    return title


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_section_at_lines(
    lines: list[str],
    start_index: int,
) -> tuple[int, str, int] | None:
    """
    Detect a section heading starting at start_index.

    Supported formats:

        1.
        Grundlagenmodule:

    or:

        4. Modul Forschungsseminar:

    Returns:

        (
            section_number,
            section_title,
            number_of_heading_lines
        )
    """

    if start_index >= len(lines):
        return None

    line = lines[start_index].strip()

    # --------------------------------------------------------
    # Format 1:
    #
    # 1.
    # Grundlagenmodule:
    # --------------------------------------------------------

    match = SECTION_NUMBER_ONLY_PATTERN.match(
        line
    )

    if match:

        if start_index + 1 >= len(lines):
            return None

        title_line = lines[
            start_index + 1
        ].strip()

        if not title_line:
            return None

        title = clean_section_title(
            title_line
        )

        return (
            int(match.group(1)),
            title,
            2,
        )

    # --------------------------------------------------------
    # Format 2:
    #
    # 4. Modul Forschungsseminar:
    # --------------------------------------------------------

    match = SECTION_INLINE_PATTERN.match(
        line
    )

    if match:

        number = int(
            match.group(1)
        )

        title = clean_section_title(
            match.group(2)
        )

        return (
            number,
            title,
            1,
        )

    return None


def find_section_in_block(
    lines: list[str],
) -> tuple[int, str, int] | None:
    """
    Search the entire block for a section heading.

    This is important because section 1 appears inside
    the same block as the § 6 heading.

    Example block:

        § 6
        Aufbau des Studiums
        (1) ...
        1.
        Grundlagenmodule:
        ...

    The parser will find:

        (1, "Grundlagenmodule", 2)
    """

    for index in range(
        len(lines)
    ):

        result = detect_section_at_lines(
            lines,
            index,
        )

        if result is None:
            continue

        number, title, consumed = result

        # Only §6 sections are valid here.
        if 1 <= number <= 6:

            return (
                number,
                title,
                consumed,
            )

    return None


# ============================================================
# MODULE EXTRACTION
# ============================================================

def extract_modules_from_text(
    text: str,
    block: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract all modules appearing in a block.

    A single block can contain many modules.

    Every module receives a reusable SourceRange
    describing its location inside the main regulation.
    """

    modules: list[dict[str, Any]] = []

    for match in MODULE_PATTERN.finditer(
        text
    ):

        # ----------------------------------------------------
        # Create main regulation source
        # ----------------------------------------------------

        main_regulation_source = (
            create_source_range(
                start_block=block
            ).to_dict()
        )

        modules.append(
            {

                # --------------------------------------------
                # Module information
                # --------------------------------------------

                "module_code": match.group(
                    "code"
                ),

                "module_name": normalize_text(
                    match.group(
                        "name"
                    )
                ),

                "credits": int(
                    match.group(
                        "credits"
                    )
                ),

                "type": normalize_text(
                    match.group(
                        "type"
                    )
                ),

                # --------------------------------------------
                # Existing block provenance
                # --------------------------------------------

                "block_index": block.get(
                    "block_index"
                ),

                "page_index": block.get(
                    "page_index"
                ),

                "page_number": block.get(
                    "page_number"
                ),

                # --------------------------------------------
                # Regulation hierarchy
                # --------------------------------------------

                "part": block.get(
                    "part"
                ),

                "part_title": block.get(
                    "part_title"
                ),

                "paragraph": block.get(
                    "paragraph"
                ),

                "paragraph_title": block.get(
                    "paragraph_title"
                ),

                # --------------------------------------------
                # Source locations
                # --------------------------------------------

                "sources": {

                    "main_regulation":
                        main_regulation_source

                },
            }
        )

    return modules


# ============================================================
# SECTION CREATION
# ============================================================

def create_section(
    number: int,
    title: str,
) -> dict[str, Any]:
    """
    Create an empty module section.
    """

    return {
        "number": number,
        "title": title,
        "blocks": [],
        "modules": [],
    }


# ============================================================
# SECTION 6 PARSER
# ============================================================

def parse_section_6(
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Parse cleaned §6 blocks.

    Important behavior:

    1. Original blocks are preserved.

    2. Section 1 can occur inside the §6 heading block.

    3. Sections can start in any line of a block.

    4. A block remains attached to the section it belongs to.

    5. "(2) Der empfohlene Ablauf..." is kept as a §6-level
       block and is NOT attached to section 6.

    6. Every extracted module receives a reusable
       main_regulation SourceRange.
    """

    sections: list[dict[str, Any]] = []

    current_section: dict[str, Any] | None = None

    overall_blocks: list[
        dict[str, Any]
    ] = []

    # --------------------------------------------------------
    # Process blocks in document order
    # --------------------------------------------------------

    for block in blocks:

        text = block.get(
            "text",
            "",
        )

        if not text:
            continue

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        # ----------------------------------------------------
        # Detect section heading
        # ----------------------------------------------------

        section_start = find_section_in_block(
            lines
        )

        # ----------------------------------------------------
        # Special handling for the first §6 block
        # ----------------------------------------------------
        #
        # Example:
        #
        # § 6
        # Aufbau des Studiums
        # (1) ...
        # 1.
        # Grundlagenmodule:
        #
        # This block belongs to section 1 because it contains
        # the beginning of section 1.
        # ----------------------------------------------------

        if section_start is not None:

            (
                section_number,
                section_title,
                _,
            ) = section_start

            # -----------------------------------------------
            # Find existing section
            # -----------------------------------------------

            existing_section = None

            for section in sections:

                if (
                    section["number"]
                    == section_number
                ):

                    existing_section = section
                    break

            # -----------------------------------------------
            # Create section if necessary
            # -----------------------------------------------

            if existing_section is None:

                current_section = create_section(
                    section_number,
                    section_title,
                )

                sections.append(
                    current_section
                )

            else:

                current_section = existing_section

            # -----------------------------------------------
            # Preserve complete original block
            # -----------------------------------------------

            current_section[
                "blocks"
            ].append(
                block
            )

            # -----------------------------------------------
            # Extract modules
            # -----------------------------------------------

            modules = extract_modules_from_text(
                text,
                block,
            )

            current_section[
                "modules"
            ].extend(
                modules
            )

            continue

        # ----------------------------------------------------
        # Paragraph (2) / remaining §6-level content
        # ----------------------------------------------------
        #
        # This block:
        #
        # (2) Der empfohlene Ablauf ...
        #
        # should NOT be attached to section 6.
        # ----------------------------------------------------

        first_line = lines[0]

        if PARAGRAPH_CONTENT_PATTERN.match(
            first_line
        ):

            overall_blocks.append(
                block
            )

            continue

        # ----------------------------------------------------
        # Normal continuation block
        # ----------------------------------------------------

        if current_section is None:

            overall_blocks.append(
                block
            )

            continue

        current_section[
            "blocks"
        ].append(
            block
        )

        modules = extract_modules_from_text(
            text,
            block,
        )

        current_section[
            "modules"
        ].extend(
            modules
        )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "sections": sections,

        "overall_blocks":
            overall_blocks,

    }