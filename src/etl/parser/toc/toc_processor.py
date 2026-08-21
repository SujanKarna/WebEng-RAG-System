"""
TOC Processor
=============

Extracts the Table of Contents from zone-detected PDF pages
and converts it into a structured representation.

This processor works directly on the output of:

    PDF extraction
        ↓
    zone detection
        ↓
    TOC processor
"""

import json
from typing import Any

from src.config.settings import TOC_PATH

from src.etl.parser.zone_detector import get_block_text

from src.etl.parser.toc.toc_parser import parse_toc


# ============================================================
# FLATTEN PAGES
# ============================================================

def flatten_blocks(
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Flatten page/block structure into a single block list.

    Text is reconstructed from the raw PDF extraction
    structure and temporarily attached as:

        block["text"]
    """

    blocks = []

    for page in pages:

        for block in page.get("blocks", []):

            # ------------------------------------------------
            # Reconstruct text from lines/spans
            # ------------------------------------------------

            text = get_block_text(block)

            # ------------------------------------------------
            # Create a shallow copy.
            #
            # We do not modify the original extraction.
            # ------------------------------------------------

            toc_block = {
                **block,
                "page_index": page.get("page_index"),
                "page_number": page.get("page_number"),
                "text": text,
            }

            blocks.append(toc_block)

    return blocks


# ============================================================
# EXTRACT TOC
# ============================================================

def extract_toc(
    pages: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Extract and structure the Table of Contents.

    Parameters
    ----------
    pages:
        Zone-detected PDF pages.

    Returns
    -------
    dict
        Structured TOC.
    """

    blocks = flatten_blocks(pages)

    toc = parse_toc(blocks)

    return toc


# ============================================================
# SAVE TOC
# ============================================================

def save_toc(
    toc: dict[str, Any],
    output_path=TOC_PATH,
) -> None:
    """
    Save structured TOC to JSON.
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