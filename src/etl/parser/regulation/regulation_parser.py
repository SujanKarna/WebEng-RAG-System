"""
Regulation Parser
=================

Builds the hierarchical structure of the main study regulation.

Input
-----

1. Cleaned blocks
2. Structured TOC
3. Optional module description index

Output
------

Teil
    ├── source
    │
    └── §
         ├── source
         ├── blocks
         └── module_sections       # §6 only
              └── modules
                   └── module_description

The parser preserves and enriches the original cleaned block
objects instead of creating new block dictionaries.

Every Part and Regulation receives a SourceRange describing
the physical location of its content in the source document.
"""

import re

from typing import Any

from src.etl.models.source import (
    create_source_range,
)

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
    """

    index: dict[str, dict[str, Any]] = {}

    for part in toc.get(
        "parts",
        [],
    ):

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

    Source is initially None and is calculated after
    all blocks have been assigned.
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
        "source": None,
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

    Every regulation receives a source range after
    blocks have been assigned.

    §6 additionally receives:

        sections
        module_sections
        overall_blocks
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
        "source": None,
        "blocks": [],
    }

    # --------------------------------------------------------
    # §6 special structure
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
# SOURCE RANGE
# ============================================================

def build_source_range(
    blocks: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Build a SourceRange from a collection of blocks.
    """

    if not blocks:
        return None

    start_block = blocks[0]

    end_block = blocks[-1]

    return create_source_range(
        start_block=start_block,
        end_block=end_block,
    ).to_dict()


# ============================================================
# ATTACH REGULATION SOURCES
# ============================================================

def attach_regulation_sources(
    result: dict[str, Any],
) -> None:
    """
    Calculate SourceRange for every Part and Regulation.
    """

    for part in result.get(
        "parts",
        [],
    ):

        part_blocks: list[
            dict[str, Any]
        ] = []

        for regulation in part.get(
            "regulations",
            [],
        ):

            regulation_blocks = (
                regulation.get(
                    "blocks",
                    [],
                )
            )

            # -----------------------------------------------
            # Regulation source
            # -----------------------------------------------

            regulation["source"] = (
                build_source_range(
                    regulation_blocks
                )
            )

            # -----------------------------------------------
            # Collect blocks for Part source
            # -----------------------------------------------

            part_blocks.extend(
                regulation_blocks
            )

        # ----------------------------------------------------
        # Part source
        # ----------------------------------------------------

        part["source"] = (
            build_source_range(
                part_blocks
            )
        )


# ============================================================
# MODULE DESCRIPTION ENRICHMENT
# ============================================================

def enrich_section_6_modules(
    section_6: dict[str, Any],
    module_description_index: dict[str, Any],
) -> tuple[int, int]:
    """
    Enrich §6 modules with their corresponding module
    descriptions using the module code as the join key.

    The module listed in §6 is the authoritative source for:

        - module_code
        - module_name
        - credits
        - type

    The module-description index provides the detailed
    module information.

    Returns:
        (
            matched_count,
            unmatched_count,
        )
    """

    matched_count = 0
    unmatched_count = 0

    # --------------------------------------------------------
    # Iterate through all §6 sections
    # --------------------------------------------------------

    for section in section_6.get(
        "sections",
        [],
    ):

        for module in section.get(
            "modules",
            [],
        ):

            module_code = module.get(
                "module_code"
            )

            if not module_code:
                unmatched_count += 1
                continue

            # ------------------------------------------------
            # Lookup module description
            # ------------------------------------------------

            description = module_description_index.get(
                module_code
            )

            if description is None:
                unmatched_count += 1
                continue


            # ------------------------------------------------
            # Convert normalized description to dictionary
            # ------------------------------------------------

            if hasattr(
                description,
                "to_dict",
            ):
                description_data = (
                    description.to_dict()
                )

            elif isinstance(
                description,
                dict,
            ):
                description_data = description.copy()

            else:
                description_data = vars(
                    description
                ).copy()

            # ------------------------------------------------
            # Extract source before cleaning description
            # ------------------------------------------------

            description_source = (
                description_data.pop(
                    "source",
                    None,
                )
            )

            # ------------------------------------------------
            # Remove fields already owned by §6 module
            # ------------------------------------------------

            description_data.pop(
                "module_code",
                None,
            )

            description_data.pop(
                "module_name",
                None,
            )

            description_data.pop(
                "credits",
                None,
            )

            # ------------------------------------------------
            # Attach clean description
            # ------------------------------------------------

            module["description"] = (
                description_data
            )

            # ------------------------------------------------
            # Attach module-description source
            # ------------------------------------------------

            if description_source is not None:

                if "sources" not in module:
                    module["sources"] = {}

                if hasattr(
                    description_source,
                    "to_dict",
                ):
                    module["sources"][
                        "module_description"
                    ] = description_source.to_dict()

                elif isinstance(
                    description_source,
                    dict,
                ):
                    module["sources"][
                        "module_description"
                    ] = description_source

                else:
                    module["sources"][
                        "module_description"
                    ] = vars(
                        description_source
                    )

            matched_count += 1

    return (
        matched_count,
        unmatched_count,
    )

# ============================================================
# PARSE REGULATIONS
# ============================================================

def parse_regulations(
    blocks: list[dict[str, Any]],
    toc: dict[str, Any],
    module_description_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Assign cleaned main-regulation blocks to the correct
    Teil and § using the TOC.

    The original cleaned block objects are preserved and
    enriched with hierarchy metadata.

    After assignment, SourceRange metadata is calculated
    for every Part and every Regulation.

    If a module description index is provided, §6 modules
    are enriched using module_code.
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

            part_structure[
                "regulations"
            ].append(
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

        paragraph_number = (
            find_paragraph_number(
                text
            )
        )

        if paragraph_number:

            location = (
                regulation_lookup.get(
                    paragraph_number
                )
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
        # Enrich ORIGINAL block
        # ----------------------------------------------------

        annotate_block(
            block=block,
            part=current_part,
            regulation=current_regulation,
        )

        # ----------------------------------------------------
        # Store SAME block object
        # ----------------------------------------------------

        current_regulation[
            "blocks"
        ].append(
            block
        )

    # ========================================================
    # ATTACH MAIN REGULATION SOURCES
    # ========================================================

    attach_regulation_sources(
        result
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
            # ------------------------------------------------

            section_6 = parse_section_6(
                regulation["blocks"]
            )

            regulation[
                "module_sections"
            ] = section_6[
                "sections"
            ]

            regulation[
                "overall_blocks"
            ] = section_6[
                "overall_blocks"
            ]

            # ------------------------------------------------
            # Enrich §6 modules their detailed
            # module descriptions.
            # ------------------------------------------------

            if module_description_index is not None:

                (
                matched_count,
                unmatched_count,
            ) = enrich_section_6_modules(
                section_6=section_6,
                module_description_index=module_description_index,
            )

            print(
                f"§6 module description enrichment: "
                f"{matched_count} matched, "
                f"{unmatched_count} unmatched"
            )

            break

    return result


# ============================================================
# PUBLIC API
# ============================================================

def structure_regulations(
    blocks: list[dict[str, Any]],
    toc: dict[str, Any],
    module_description_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Public entry point.

    Keeps main.py clean.
    """

    return parse_regulations(
        blocks=blocks,
        toc=toc,
        module_description_index=module_description_index,
    )