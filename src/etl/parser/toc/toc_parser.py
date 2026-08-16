import re
from typing import Any


# ============================================================
# REGULAR EXPRESSIONS
# ============================================================

PART_PATTERN = re.compile(
    r"^\s*(Teil\s+\d+)\s*:?\s*(.*?)\s*$",
    re.IGNORECASE,
)

PARAGRAPH_PATTERN = re.compile(
    r"§\s*\d+"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize whitespace.

    Example:

        Studienbeginn und
        Regelstudienzeit

    becomes:

        Studienbeginn und Regelstudienzeit
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


# ============================================================
# PART DETECTION
# ============================================================

def is_part(text: str) -> bool:
    """
    Return True if the text represents a Teil heading.
    """

    return (
        PART_PATTERN.match(
            normalize_text(text)
        )
        is not None
    )


def parse_part(text: str) -> dict[str, str]:
    """
    Parse a Teil heading.

    Example:

        Teil 1 Allgemeine Bestimmungen

    returns:

        {
            "part": "Teil 1",
            "title": "Allgemeine Bestimmungen"
        }
    """

    text = normalize_text(text)

    match = PART_PATTERN.match(text)

    if not match:
        raise ValueError(
            f"Invalid Teil heading: {text}"
        )

    return {
        "part": normalize_text(
            match.group(1)
        ),
        "title": normalize_text(
            match.group(2)
        ),
    }


# ============================================================
# PARAGRAPH PARSING
# ============================================================

def parse_paragraphs(
    text: str,
) -> list[dict[str, str]]:
    """
    Extract all § entries from a single text block.

    Example:

        § 1 Geltungsbereich
        § 2 Studienbeginn und Regelstudienzeit
        § 3 Zugangsvoraussetzungen

    becomes:

        [
            {
                "paragraph": "§ 1",
                "title": "Geltungsbereich"
            },
            {
                "paragraph": "§ 2",
                "title": "Studienbeginn und Regelstudienzeit"
            },
            {
                "paragraph": "§ 3",
                "title": "Zugangsvoraussetzungen"
            }
        ]
    """

    text = normalize_text(text)

    matches = list(
        PARAGRAPH_PATTERN.finditer(text)
    )

    paragraphs = []

    for index, match in enumerate(matches):

        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        entry = text[start:end].strip()

        paragraph_match = re.match(
            r"^(§\s*\d+)\s*(.*)$",
            entry,
        )

        if not paragraph_match:
            continue

        paragraph_number = normalize_text(
            paragraph_match.group(1)
        )

        title = normalize_text(
            paragraph_match.group(2)
        )

        paragraphs.append(
            {
                "paragraph": paragraph_number,
                "title": title,
            }
        )

    return paragraphs


# ============================================================
# TOC PARSER
# ============================================================

def parse_toc(
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Parse TOC blocks into a hierarchical structure.

    Expected result:

        {
            "parts": [
                {
                    "part": "Teil 1",
                    "title": "Allgemeine Bestimmungen",
                    "regulations": [
                        {
                            "paragraph": "§ 1",
                            "title": "Geltungsbereich"
                        }
                    ]
                }
            ]
        }
    """

    toc = {
        "parts": []
    }

    current_part = None

    for block in blocks:

        text = normalize_text(
            block.get("text", "")
        )

        if not text:
            continue

        # --------------------------------------------------------
        # Ignore TOC heading
        # --------------------------------------------------------

        if text.lower() == "inhaltsübersicht":
            continue

        # --------------------------------------------------------
        # Detect Teil
        # --------------------------------------------------------

        if is_part(text):

            current_part = parse_part(text)

            current_part["regulations"] = []

            toc["parts"].append(
                current_part
            )

            continue

        # --------------------------------------------------------
        # Detect § entries
        # --------------------------------------------------------

        if current_part is None:
            continue

        paragraphs = parse_paragraphs(
            text
        )

        current_part["regulations"].extend(
            paragraphs
        )

    return toc