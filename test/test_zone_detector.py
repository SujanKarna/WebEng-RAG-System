"""
Test the document zone detector.

This test prints every zone transition and the final
zone distribution.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

from src.etl.parser.zone_detector import detect_zones


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
# HELPERS
# ============================================================

def get_block_text(block):
    """
    Reconstruct block text for display.
    """

    parts = []

    for line in block.get("lines", []):

        text = "".join(
            span.get("text", "")
            for span in line.get("spans", [])
        )

        if text.strip():
            parts.append(text.strip())

    return " ".join(parts)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load extraction
    # --------------------------------------------------------

    with EXTRACTION_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        pages = json.load(file)

    print("=" * 80)
    print("DOCUMENT ZONE DETECTOR TEST")
    print("=" * 80)

    print()
    print(f"Extraction file:")
    print(f"  {EXTRACTION_PATH}")

    print()
    print(f"Total pages: {len(pages)}")

    # --------------------------------------------------------
    # Remember original zones so we can detect transitions.
    # --------------------------------------------------------

    previous_zone = None

    transitions = []

    # --------------------------------------------------------
    # Detect zones
    # --------------------------------------------------------

    pages = detect_zones(pages)

    # --------------------------------------------------------
    # Inspect transitions
    # --------------------------------------------------------

    for page in pages:

        page_number = page.get(
            "page_number",
            page.get("page_index", 0) + 1,
        )

        for block in page.get("blocks", []):

            zone = block.get("zone")

            if zone != previous_zone:

                transitions.append(
                    {
                        "page": page_number,
                        "block": block.get(
                            "block_index"
                        ),
                        "zone": zone,
                        "text": get_block_text(block),
                    }
                )

                previous_zone = zone

    # --------------------------------------------------------
    # Print transitions
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("ZONE TRANSITIONS")
    print("=" * 80)

    for index, transition in enumerate(
        transitions,
        start=1,
    ):

        print()
        print(f"[TRANSITION {index}]")

        print(
            f"Page       : "
            f"{transition['page']}"
        )

        print(
            f"Block      : "
            f"{transition['block']}"
        )

        print(
            f"New zone   : "
            f"{transition['zone']}"
        )

        print(
            f"Text       : "
            f"{transition['text'][:500]}"
        )

    # --------------------------------------------------------
    # Count blocks per zone.
    # --------------------------------------------------------

    zone_counts = Counter()

    for page in pages:

        for block in page.get("blocks", []):

            zone = block.get("zone")

            zone_counts[zone] += 1

    # --------------------------------------------------------
    # Print distribution.
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("ZONE DISTRIBUTION")
    print("=" * 80)

    for zone, count in zone_counts.items():

        print(
            f"{zone:<25}: "
            f"{count:>6} blocks"
        )

    # --------------------------------------------------------
    # Determine pages per zone.
    # --------------------------------------------------------

    zone_pages = defaultdict(set)

    for page in pages:

        page_number = page.get(
            "page_number",
            page.get("page_index", 0) + 1,
        )

        for block in page.get("blocks", []):

            zone = block.get("zone")

            zone_pages[zone].add(
                page_number
            )

    # --------------------------------------------------------
    # Print pages per zone.
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("PAGES PER ZONE")
    print("=" * 80)

    for zone, page_numbers in zone_pages.items():

        sorted_pages = sorted(
            page_numbers
        )

        print()
        print(
            f"{zone:<25}: "
            f"{len(sorted_pages):>3} pages"
        )

        print(
            f"  Pages: {sorted_pages}"
        )

    print()
    print("=" * 80)
    print("ZONE DETECTION TEST COMPLETE")
    print("=" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()