"""
TOC Processor
=============

Responsible for:

1. Selecting blocks belonging to the TOC zone.
2. Reconstructing their text from raw extraction data.
3. Calling the TOC parser.
4. Saving the resulting TOC JSON.
"""

import json
from pathlib import Path
from typing import Any

from src.etl.parser.zone_detector import (
    get_block_text,
)

from src.etl.parser.toc.toc_parser import (
    parse_toc,
)


# ============================================================
# TOC BLOCK EXTRACTION
# ============================================================

def extract_toc_blocks(
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Extract TOC blocks and reconstruct their text.

    Raw extraction stores text inside:

        block
            └── lines
                  └── spans
                        └── text

    The TOC parser expects:

        {
            "zone": "table_of_contents",
            "text": "..."
        }
    """

    toc_blocks = []

    for page in pages:

        for block in page.get(
            "blocks",
            [],
        ):

            if (
                block.get("zone")
                != "table_of_contents"
            ):
                continue

            text = get_block_text(
                block
            )

            if not text:
                continue

            # ------------------------------------------------
            # Create parser-ready block
            # ------------------------------------------------

            toc_blocks.append(
                {
                    "page_index": page.get(
                        "page_index"
                    ),
                    "page_number": page.get(
                        "page_number"
                    ),
                    "block_index": block.get(
                        "block_index"
                    ),
                    "zone": block.get(
                        "zone"
                    ),
                    "text": text,
                }
            )

    return toc_blocks


# ============================================================
# TOC PROCESSING
# ============================================================

def process_toc(
    pages: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Extract and parse the TOC.
    """

    toc_blocks = extract_toc_blocks(
        pages
    )

    return parse_toc(
        toc_blocks
    )


# ============================================================
# SAVE TOC
# ============================================================

def save_toc(
    toc: dict[str, Any],
    output_path: Path,
) -> None:
    """
    Save parsed TOC as JSON.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            toc,
            file,
            indent=2,
            ensure_ascii=False,
        )