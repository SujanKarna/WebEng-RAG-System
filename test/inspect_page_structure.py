"""
Inspect the high-level structure of the TU Chemnitz
Web Engineering 2025 study regulation.

This script is for investigation only.

It does NOT modify the extracted JSON.

The goal is to identify the boundaries between:

    INTRODUCTION
    TABLE_OF_CONTENTS
    MAIN_REGULATIONS
    STUDY_PLAN
    MODULE_DESCRIPTIONS
"""

from pathlib import Path
import json


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXTRACTION_PATH = (
    PROJECT_ROOT
    / "data"
    / "extracted"
    / "tu_chemnitz_web_engineering_2025_raw.json"
)


# ============================================================
# TEXT EXTRACTION
# ============================================================

def get_block_text(block: dict) -> str:
    """
    Reconstruct the text contained in one extracted block.

    The raw extraction stores text inside:

        block
          └── lines
                └── spans
                      └── text
    """

    lines = block.get(
        "lines",
        []
    )

    text_parts = []

    for line in lines:

        spans = line.get(
            "spans",
            []
        )

        line_text = "".join(
            span.get(
                "text",
                ""
            )
            for span in spans
        )

        if line_text.strip():

            text_parts.append(
                line_text.strip()
            )

    return " ".join(
        text_parts
    )


def get_page_text(page: dict) -> str:
    """
    Reconstruct all textual content from a page.
    """

    blocks = page.get(
        "blocks",
        []
    )

    texts = []

    for block in blocks:

        # PyMuPDF text block.
        #
        # Type 0 = text.
        # Other types can be images/vector content.

        if block.get(
            "type"
        ) != 0:

            continue

        text = get_block_text(
            block
        )

        if text:

            texts.append(
                text
            )

    return "\n".join(
        texts
    )


# ============================================================
# PAGE PREVIEW
# ============================================================

def get_preview(
    page: dict,
    max_lines: int = 8,
) -> list[str]:
    """
    Return the first meaningful lines of a page.

    This is only for terminal inspection.
    """

    text = get_page_text(
        page
    )

    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        lines.append(
            line
        )

        if len(lines) >= max_lines:
            break

    return lines


# ============================================================
# DOCUMENT INSPECTION
# ============================================================

def inspect_pages(
    extraction_path: Path,
) -> None:
    """
    Inspect every page of the extracted document.
    """

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not extraction_path.exists():

        raise FileNotFoundError(
            f"Extraction file not found:\n"
            f"{extraction_path}"
        )

    # --------------------------------------------------------
    # LOAD JSON
    # --------------------------------------------------------

    with extraction_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        document = json.load(
            file
        )

    # --------------------------------------------------------
    # HANDLE ROOT STRUCTURE
    # --------------------------------------------------------

    if isinstance(
        document,
        list
    ):

        # Your extractor currently produces:
        #
        # [
        #     page,
        #     page,
        #     page,
        #     ...
        # ]

        pages = document

    elif isinstance(
        document,
        dict
    ):

        # Also support:
        #
        # {
        #     "pages": [...]
        # }

        pages = document.get(
            "pages",
            []
        )

    else:

        raise TypeError(
            "Unexpected extraction JSON structure. "
            "Expected a list or dictionary."
        )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if not isinstance(
        pages,
        list
    ):

        raise TypeError(
            "The extracted pages must be stored as a list."
        )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("DOCUMENT STRUCTURE INSPECTION")
    print("=" * 80)

    print(
        f"Extraction file:"
    )

    print(
        f"  {extraction_path}"
    )

    print()

    print(
        f"Total pages: {len(pages)}"
    )

    print()

    # --------------------------------------------------------
    # PAGE LOOP
    # --------------------------------------------------------

    for page in pages:

        page_number = page.get(
            "page_number"
        )

        if page_number is None:

            page_number = (
                page.get(
                    "page_index",
                    0
                )
                + 1
            )

        preview = get_preview(
            page
        )

        print()
        print("=" * 80)

        print(
            f"PAGE {page_number}"
        )

        print("-" * 80)

        if not preview:

            print(
                "[NO TEXT]"
            )

            continue

        for line in preview:

            # Prevent extremely long lines
            # from flooding the terminal.

            if len(line) > 160:

                line = (
                    line[:160]
                    + "..."
                )

            print(
                line
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    inspect_pages(
        EXTRACTION_PATH
    )