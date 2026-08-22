"""
Module Description Parser
=========================

Pipeline:

    cleaned blocks
        ↓
    merge_module_blocks()
        ↓
    parse_module_descriptions()
        ↓
    ModuleDescription

The merger creates one large text block per module.

The parser extracts structured fields from that merged text.
"""

import re
from typing import Any

from src.etl.models.module_description import ModuleDescription
from src.etl.models.source import create_source_range


# ============================================================
# CONSTANTS
# ============================================================

MODULE_DESCRIPTION_ZONE = "module_descriptions"


# ============================================================
# MODULE NUMBER
# ============================================================

MODULE_NUMBER_PATTERN = re.compile(
    r"Modulnummer\s+"
    r"(?P<code>\d{6}-\d{3})"
    r"\s*"
    r"\(?"
    r"Version\s+"
    r"(?P<version>\d+)"
    r"\)?",
    re.IGNORECASE,
)


# ============================================================
# CATEGORIES
# ============================================================

CATEGORIES = {
    "Grundlagenmodul",
    "Vertiefungsmodul",
    "Modul Schlüsselkompetenzen",
    "Modul Forschungsseminar",
    "Challengemodul",
    "Modul Master-Arbeit",
}


# ============================================================
# FIELD HEADINGS
# ============================================================

FIELD_HEADINGS = {
    "Modulname": "module_name",

    "Modulverantwortlich": "responsible",

    "Lehrformen": "teaching_forms",

    "Voraussetzungen für die Teilnahme "
    "(empfohlene Kenntnisse und Fähigkeiten)":
        "prerequisites",

    "Verwendbarkeit des Moduls":
        "applicability",

    "Voraussetzungen für die Vergabe von "
    "Leistungspunkten":
        "credit_requirements",

    "Modulprüfung":
        "examination",

    "Leistungspunkte und Noten":
        "credits_and_grades",

    "Häufigkeit des Angebots":
        "frequency",

    "Arbeitsaufwand":
        "workload",

    "Dauer des Moduls":
        "duration",
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Collapse whitespace into single spaces.
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def normalize_heading(text: str) -> str:
    return normalize_text(
        text
    ).rstrip(":")


# ============================================================
# CATEGORY
# ============================================================

def is_category(text: str) -> bool:

    return normalize_text(
        text
    ) in CATEGORIES


# ============================================================
# MODULE NUMBER
# ============================================================

def parse_module_number(
    text: str,
) -> tuple[str, str] | None:

    normalized = normalize_text(
        text
    )

    match = MODULE_NUMBER_PATTERN.search(
        normalized
    )

    if not match:
        return None

    return (
        match.group("code"),
        match.group("version"),
    )


# ============================================================
# MERGE MODULE BLOCKS
# ============================================================

def merge_module_blocks(
    blocks: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    merged_modules: list[
        dict[str, Any]
    ] = []

    current_blocks: list[
        dict[str, Any]
    ] = []

    current_category: str | None = None

    for block in blocks:

        if block.get(
            "zone"
        ) != MODULE_DESCRIPTION_ZONE:
            continue

        text = block.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        normalized = normalize_text(
            text
        )

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        if is_category(
            normalized
        ):

            current_category = normalized

            continue

        # ----------------------------------------------------
        # MODULE START
        # ----------------------------------------------------

        module_info = parse_module_number(
            text
        )

        if module_info:

            if current_blocks:

                merged_modules.append(
                    _create_merged_module_block(
                        current_blocks,
                        current_category,
                    )
                )

            current_blocks = [
                block
            ]

            continue

        # ----------------------------------------------------
        # MODULE CONTENT
        # ----------------------------------------------------

        if current_blocks:

            current_blocks.append(
                block
            )

    # --------------------------------------------------------
    # FINAL MODULE
    # --------------------------------------------------------

    if current_blocks:

        merged_modules.append(
            _create_merged_module_block(
                current_blocks,
                current_category,
            )
        )

    return merged_modules


# ============================================================
# CREATE MERGED BLOCK
# ============================================================

def _create_merged_module_block(
    blocks: list[dict[str, Any]],
    category: str | None,
) -> dict[str, Any]:

    first_block = blocks[0]

    last_block = blocks[-1]

    merged_text = "\n\n".join(
        block.get(
            "text",
            "",
        ).strip()

        for block in blocks

        if block.get(
            "text",
            "",
        ).strip()
    )

    merged_text = clean_merged_module_text(
        merged_text
    )

    return {
        "text": merged_text,

        "zone":
            MODULE_DESCRIPTION_ZONE,

        "category":
            category,

        "module_start_block":
            first_block,

        "module_end_block":
            last_block,

        "source":
            create_source_range(
                start_block=first_block,
                end_block=last_block,
            ),
    }


# ============================================================
# CLEAN MERGED MODULE TEXT
# ============================================================

def clean_merged_module_text(
    text: str,
) -> str:

    lines = text.splitlines()

    cleaned: list[str] = []

    skip_header_continuation = False

    for line in lines:

        normalized = normalize_text(
            line
        )

        if not normalized:

            cleaned.append("")

            continue

        # ----------------------------------------------------
        # PDF HEADER
        # ----------------------------------------------------

        if normalized.startswith(
            "Anlage 2: Modulbeschreibung zum "
            "englischsprachigen"
        ):

            skip_header_continuation = True

            continue

        if skip_header_continuation:

            if normalized == (
                "dem Abschluss Master of Science"
            ):

                skip_header_continuation = False

                continue

            skip_header_continuation = False

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        if normalized == (
            "Amtliche Bekanntmachungen"
        ):
            continue

        if re.fullmatch(
            r"_+",
            normalized,
        ):
            continue

        if re.fullmatch(
            r"Nr\. \d+/\d+",
            normalized,
        ):
            continue

        if re.fullmatch(
            r"vom \d{1,2}\. "
            r"\w+ \d{4}",
            normalized,
            re.IGNORECASE,
        ):
            continue

        if re.fullmatch(
            r"\d{3,4}",
            normalized,
        ):
            continue

        cleaned.append(
            line
        )

    return "\n".join(
        cleaned
    ).strip()


# ============================================================
# NORMALIZE MODULE TEXT
# ============================================================

def normalize_module_text(text: str) -> str:

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    text = "\n".join(lines)

    # --------------------------------------------------------
    # Multi-line headings
    # --------------------------------------------------------

    text = re.sub(
        r"Inhalte\s+und\s+Qualifikationsziele",
        "Inhalte und Qualifikationsziele",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"Voraussetzungen\s+für\s+die\s+Teilnahme\s+"
        r"\(empfohlene\s+Kenntnisse\s+und\s+Fähigkeiten\)",
        "Voraussetzungen für die Teilnahme "
        "(empfohlene Kenntnisse und Fähigkeiten)",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"Voraussetzungen\s+für\s+die\s+Vergabe\s+von\s+"
        r"Leistungspunkten",
        "Voraussetzungen für die Vergabe von "
        "Leistungspunkten",
        text,
        flags=re.IGNORECASE,
    )

    return text


# ============================================================
# FIELD HEADING PATTERNS
# ============================================================

def build_field_patterns() -> list[
    tuple[str, str, re.Pattern]
]:

    patterns = []

    for heading, field_name in FIELD_HEADINGS.items():

        pattern = re.compile(
            r"(?m)^"
            + re.escape(
                heading
            )
            + r"\s*$",
            re.IGNORECASE,
        )

        patterns.append(
            (
                heading,
                field_name,
                pattern,
            )
        )

    return patterns


FIELD_PATTERNS = build_field_patterns()


# ============================================================
# FIND FIELD POSITIONS
# ============================================================

def find_field_positions(
    text: str,
) -> list[tuple[int, int, str]]:

    positions = []

    # --------------------------------------------------------
    # NORMAL FIELD HEADINGS
    # --------------------------------------------------------

    for (
        heading,
        field_name,
        pattern,
    ) in FIELD_PATTERNS:

        for match in pattern.finditer(text):

            positions.append(
                (
                    match.start(),
                    match.end(),
                    field_name,
                )
            )

    # --------------------------------------------------------
    # CONTENT SECTION HEADING
    #
    # This is NOT a ModuleDescription field.
    # It is only a structural boundary.
    # --------------------------------------------------------

    content_section_pattern = re.compile(
        r"(?m)^Inhalte\s+und\s+Qualifikationsziele\s*$",
        re.IGNORECASE,
    )

    for match in content_section_pattern.finditer(text):

        positions.append(
            (
                match.start(),
                match.end(),
                "__section__",
            )
        )

    # --------------------------------------------------------
    # SORT BY POSITION
    # --------------------------------------------------------

    positions.sort(
        key=lambda item: item[0]
    )

    return positions


# ============================================================
# EXTRACT FIELD VALUES
# ============================================================

def extract_fields(
    text: str,
) -> dict[str, str]:

    positions = find_field_positions(text)

    fields: dict[str, str] = {}

    for index, (
        start,
        end,
        field_name,
    ) in enumerate(positions):

        if index + 1 < len(positions):

            next_start = positions[
                index + 1
            ][0]

        else:

            next_start = len(text)

        value = text[
            end:next_start
        ].strip()

        # ----------------------------------------------------
        # Structural boundary
        # ----------------------------------------------------

        if field_name == "__section__":
            continue

        value = clean_field_value(
            value
        )

        if value is not None:
            fields[field_name] = value

    return fields


# ============================================================
# CLEAN FIELD VALUE
# ============================================================

def clean_field_value(
    value: str | None,
) -> str | None:

    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    if value == "---":
        return None

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    value = normalize_text(
        value
    )

    return value or None


# ============================================================
# EXTRACT CONTENT + GOALS
# ============================================================

def extract_content_and_goals(
    text: str,
) -> tuple[str | None, str | None]:

    content_match = re.search(
        r"(?m)^Inhalte:\s*$",
        text,
        flags=re.IGNORECASE,
    )

    goals_match = re.search(
        r"(?m)^Qualifikationsziele:\s*$",
        text,
        flags=re.IGNORECASE,
    )

    if not content_match:
        return None, None

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    if goals_match:
        content = text[
            content_match.end():
            goals_match.start()
        ]

        goals = text[
            goals_match.end():
        ]

    else:
        content = text[
            content_match.end():
        ]

        goals = ""

    content = clean_field_value(content)
    goals = clean_field_value(goals)

    return content, goals


# ============================================================
# EXTRACT CONTENT SECTION
# ============================================================

def extract_content_section(
    text: str,
) -> str | None:

    heading_match = re.search(
        r"(?m)^Inhalte und "
        r"Qualifikationsziele\s*$",
        text,
        flags=re.IGNORECASE,
    )

    if not heading_match:
        return None

    start = heading_match.end()

    positions = find_field_positions(text)

    next_positions = [
        position
        for position in positions
        if position[0] > start
    ]

    if next_positions:
        end = next_positions[0][0]
    else:
        end = len(text)

    return text[start:end].strip()


# ============================================================
# PARSE ONE MERGED MODULE
# ============================================================

def parse_merged_module(
    merged_block: dict[str, Any],
) -> ModuleDescription:

    raw_text = merged_block[
        "text"
    ]
    print("\n" + "=" * 80)
    print("RAW MERGED MODULE")
    print("=" * 80)
    print(raw_text)
    print("=" * 80)
    # --------------------------------------------------------
    # Normalize text
    # --------------------------------------------------------

    text = normalize_module_text(
        raw_text
    )

    # --------------------------------------------------------
    # Module number
    # --------------------------------------------------------

    module_info = parse_module_number(
        text
    )

    if module_info is None:

        raise ValueError(
            "Could not find module number."
        )

    code, version = module_info

    # --------------------------------------------------------
    # Extract normal fields
    # --------------------------------------------------------

    fields = extract_fields(
        text
    )

    # --------------------------------------------------------
    # Content / qualification goals
    # --------------------------------------------------------

    content_section = (
        extract_content_section(
            text
        )
    )

    content = None

    qualification_goals = None

    if content_section:

        (
            content,
            qualification_goals,
        ) = extract_content_and_goals(
            content_section
        )

    # ========================================================
    # CREATE MODEL
    # ========================================================

    return ModuleDescription(

        module_code=code,

        module_name=(
            fields.get(
                "module_name"
            )
            or ""
        ),

        category=(
            merged_block.get(
                "category"
            )
            or ""
        ),

        version=version,

        responsible=fields.get(
            "responsible"
        ),

        content=content,

        qualification_goals=(
            qualification_goals
        ),

        teaching_forms=fields.get(
            "teaching_forms"
        ),

        prerequisites=fields.get(
            "prerequisites"
        ),

        applicability=fields.get(
            "applicability"
        ),

        credit_requirements=fields.get(
            "credit_requirements"
        ),

        examination=fields.get(
            "examination"
        ),

        credits_and_grades=fields.get(
            "credits_and_grades"
        ),

        frequency=fields.get(
            "frequency"
        ),

        workload=fields.get(
            "workload"
        ),

        duration=fields.get(
            "duration"
        ),

        source=merged_block.get(
            "source"
        ),
    )


# ============================================================
# PARSE ALL MODULE DESCRIPTIONS
# ============================================================

def parse_module_descriptions(
    merged_modules: list[
        dict[str, Any]
    ],
) -> list[ModuleDescription]:

    modules: list[
        ModuleDescription
    ] = []

    for merged_block in merged_modules:

        try:

            module = parse_merged_module(
                merged_block
            )

            modules.append(
                module
            )

        except Exception as exc:

            print(
                "ERROR parsing module:"
            )

            print(
                exc
            )

    return modules