# test/find_toc_marker.py

from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXTRACTION_PATH = (
    PROJECT_ROOT
    / "data"
    / "extracted"
    / "tu_chemnitz_web_engineering_2025_raw.json"
)


TOC_MARKERS = [
    "Inhaltsübersicht",
    "Inhaltsverzeichnis",
]


def get_block_text(block):
    texts = []

    for line in block.get("lines", []):

        line_text = "".join(
            span.get("text", "")
            for span in line.get("spans", [])
        )

        if line_text.strip():
            texts.append(line_text.strip())

    return " ".join(texts)


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


print("=" * 80)
print("TOC MARKER SEARCH")
print("=" * 80)


for page in pages:

    page_number = page.get(
        "page_number",
        page.get("page_index", 0) + 1,
    )

    for block in page.get("blocks", []):

        if block.get("type") != 0:
            continue

        text = get_block_text(block)

        for marker in TOC_MARKERS:

            if marker.lower() in text.lower():

                print()
                print(f"PAGE: {page_number}")
                print(f"MARKER: {marker}")
                print(f"BLOCK: {text}")