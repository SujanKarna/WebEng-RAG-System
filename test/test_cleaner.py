"""
Cleaner Test
============

Runs:

    raw extraction
        ↓
    zone detection
        ↓
    cleaner

The result is inspected but not saved yet.
"""

import json
from pathlib import Path
from collections import Counter

from src.etl.parser.zone_detector import detect_zones
from src.etl.parser.cleaner import clean


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
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("DOCUMENT CLEANER TEST")
    print("=" * 80)

    # --------------------------------------------------------
    # Load extraction
    # --------------------------------------------------------

    with EXTRACTION_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        pages = json.load(file)

    print()
    print(
        f"Raw pages: {len(pages)}"
    )

    # --------------------------------------------------------
    # Run zone detection.
    #
    # This adds:
    #
    #     block["zone"]
    #
    # to every block.
    # --------------------------------------------------------

    pages = detect_zones(
        pages
    )

    # --------------------------------------------------------
    # Count raw blocks.
    # --------------------------------------------------------

    raw_block_count = sum(
        len(
            page.get(
                "blocks",
                [],
            )
        )
        for page in pages
    )

    print(
        f"Raw blocks: {raw_block_count}"
    )

    # --------------------------------------------------------
    # Run cleaner.
    # --------------------------------------------------------

    cleaned_blocks = clean(
        pages
    )

    print(
        f"Clean blocks: "
        f"{len(cleaned_blocks)}"
    )

    # --------------------------------------------------------
    # Distribution of cleaned blocks.
    # --------------------------------------------------------

    zone_counts = Counter(
        block.zone
        for block in cleaned_blocks
    )

    print()
    print("=" * 80)
    print("CLEANED BLOCK DISTRIBUTION")
    print("=" * 80)

    for zone, count in zone_counts.items():

        print(
            f"{zone:<25}: "
            f"{count:>6} blocks"
        )

    # --------------------------------------------------------
    # Page distribution.
    # --------------------------------------------------------

    page_counts = Counter(
        block.page_number
        for block in cleaned_blocks
    )

    print()
    print("=" * 80)
    print("CLEANED PAGE RANGE")
    print("=" * 80)

    if page_counts:

        print(
            f"First page: "
            f"{min(page_counts)}"
        )

        print(
            f"Last page : "
            f"{max(page_counts)}"
        )

    # --------------------------------------------------------
    # Inspect first 10 cleaned blocks.
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("FIRST 10 CLEANED BLOCKS")
    print("=" * 80)

    for index, block in enumerate(
        cleaned_blocks[:10],
        start=1,
    ):

        print()
        print(
            f"[BLOCK {index}]"
        )

        print(
            f"Page : "
            f"{block.page_number}"
        )

        print(
            f"Zone : "
            f"{block.zone}"
        )

        print(
            f"Text : "
            f"{block.text[:500]}"
        )

    # --------------------------------------------------------
    # Inspect last 10 blocks.
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("LAST 10 CLEANED BLOCKS")
    print("=" * 80)

    for index, block in enumerate(
        cleaned_blocks[-10:],
        start=1,
    ):

        print()
        print(
            f"[BLOCK {index}]"
        )

        print(
            f"Page : "
            f"{block.page_number}"
        )

        print(
            f"Zone : "
            f"{block.zone}"
        )

        print(
            f"Text : "
            f"{block.text[:500]}"
        )

    print()
    print("=" * 80)
    print("CLEANER TEST COMPLETE")
    print("=" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()