from pathlib import Path
from collections import Counter
import json

from src.etl.parser.zone_detector import (
    assign_zones,
    get_block_text,
)


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
# MAIN TEST
# ============================================================

def main():

    print("=" * 80)
    print("DOCUMENT ZONE DETECTOR TEST")
    print("=" * 80)

    print()
    print("Extraction file:")
    print(f"  {EXTRACTION_PATH}")

    # --------------------------------------------------------
    # LOAD RAW EXTRACTION
    # --------------------------------------------------------

    with EXTRACTION_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        document = json.load(file)

    # --------------------------------------------------------
    # HANDLE BOTH POSSIBLE JSON STRUCTURES
    # --------------------------------------------------------
    #
    # Your extraction currently appears to be a list of pages.
    #
    # But this also supports:
    #
    # {
    #     "pages": [...]
    # }
    #
    # This makes the test more robust.
    # --------------------------------------------------------

    if isinstance(document, list):

        pages = document

    elif isinstance(document, dict):

        pages = document.get(
            "pages",
            []
        )

    else:

        raise ValueError(
            "Unexpected extraction JSON structure."
        )

    print()
    print(f"Total pages: {len(pages)}")

    # --------------------------------------------------------
    # RUN ZONE DETECTOR
    # --------------------------------------------------------

    zoned_pages = assign_zones(
        pages
    )

    # --------------------------------------------------------
    # DETECT TRANSITIONS
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("ZONE TRANSITIONS")
    print("=" * 80)

    previous_zone = None

    transition_number = 0

    for page in zoned_pages:

        page_number = page.get(
            "page_number",
            page.get(
                "page_index",
                0
            ) + 1
        )

        for block in page.get(
            "blocks",
            []
        ):

            zone = block.get(
                "zone",
                "unknown"
            )

            # Only print when the zone changes.

            if zone != previous_zone:

                transition_number += 1

                text = get_block_text(
                    block
                )

                print()
                print(
                    f"[TRANSITION {transition_number}]"
                )

                print(
                    f"Page       : {page_number}"
                )

                print(
                    f"Block      : "
                    f"{block.get('block_index')}"
                )

                print(
                    f"New zone   : {zone}"
                )

                print(
                    f"Text       : {text[:300]}"
                )

                previous_zone = zone

    # --------------------------------------------------------
    # COUNT BLOCKS BY ZONE
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("ZONE DISTRIBUTION")
    print("=" * 80)

    zone_counts = Counter()

    for page in zoned_pages:

        for block in page.get(
            "blocks",
            []
        ):

            zone = block.get(
                "zone",
                "unknown"
            )

            zone_counts[zone] += 1

    for zone, count in zone_counts.items():

        print(
            f"{zone:<25} : {count:>5} blocks"
        )

    # --------------------------------------------------------
    # COUNT PAGES CONTAINING EACH ZONE
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("PAGES PER ZONE")
    print("=" * 80)

    zone_pages = {}

    for page in zoned_pages:

        page_number = page.get(
            "page_number",
            page.get(
                "page_index",
                0
            ) + 1
        )

        zones_on_page = set()

        for block in page.get(
            "blocks",
            []
        ):

            zones_on_page.add(
                block.get(
                    "zone",
                    "unknown"
                )
            )

        for zone in zones_on_page:

            zone_pages.setdefault(
                zone,
                []
            ).append(
                page_number
            )

    for zone, page_numbers in zone_pages.items():

        print(
            f"{zone:<25} : "
            f"{len(page_numbers):>3} pages"
        )

        print(
            f"  Pages: {page_numbers}"
        )

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("ZONE DETECTION TEST COMPLETE")
    print("=" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()