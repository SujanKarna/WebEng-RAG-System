"""
Find actual structural zone markers in the extracted document.

This test searches for occurrences of Anlage 1, Anlage 2,
STUDIENABLAUFPLAN and Modulbeschreibungen and prints their
page, block and surrounding text.

It does NOT modify the extraction.
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


SEARCH_TERMS = [
    "Anlage 1",
    "STUDIENABLAUFPLAN",
    "Anlage 2",
    "Modulbeschreibungen",
]


# ============================================================
# HELPERS
# ============================================================

def get_block_text(block):
    """
    Reconstruct the text of an extracted block.
    """

    parts = []

    for line in block.get("lines", []):

        line_text = "".join(
            span.get("text", "")
            for span in line.get("spans", [])
        )

        if line_text.strip():
            parts.append(
                line_text.strip()
            )

    return " ".join(parts)


# ============================================================
# MAIN
# ============================================================

def main():

    with EXTRACTION_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        document = json.load(file)

    pages = (
        document
        if isinstance(document, list)
        else document.get("pages", [])
    )

    print("=" * 100)
    print("ZONE MARKER INSPECTION")
    print("=" * 100)

    for term in SEARCH_TERMS:

        print()
        print("=" * 100)
        print(f"SEARCH TERM: {term}")
        print("=" * 100)

        found = False

        for page in pages:

            page_number = page.get(
                "page_number",
                page.get("page_index", 0) + 1,
            )

            for block in page.get(
                "blocks",
                []
            ):

                text = get_block_text(
                    block
                )

                if term.lower() in text.lower():

                    found = True

                    print()
                    print(
                        f"Page  : {page_number}"
                    )

                    print(
                        f"Block : "
                        f"{block.get('block_index')}"
                    )

                    print(
                        f"Text  : {text}"
                    )

        if not found:

            print("No occurrences found.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()