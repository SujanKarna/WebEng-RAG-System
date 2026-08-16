import re
from pathlib import Path
from typing import Any


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving meaningful
    paragraph/line separation.

    Examples
    --------
    Multiple spaces:
        "Web    Engineering"
        ->
        "Web Engineering"

    Tabs:
        "Web\\tEngineering"
        ->
        "Web Engineering"

    Excessive blank lines:
        "A\\n\\n\\nB"
        ->
        "A\\n\\nB"
    """

    # Normalize different newline representations.

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # Replace tabs with spaces.

    text = text.replace(
        "\t",
        " ",
    )

    # Remove trailing whitespace from every line.

    lines = [
        line.rstrip()
        for line in text.split("\n")
    ]

    # Remove leading/trailing whitespace from every line.

    lines = [
        line.strip()
        for line in lines
    ]

    # Collapse repeated spaces inside each line.

    lines = [
        re.sub(
            r"[ ]{2,}",
            " ",
            line,
        )
        for line in lines
    ]

    # Collapse more than two consecutive blank lines.

    cleaned_lines = []

    previous_blank = False

    for line in lines:

        is_blank = not line

        if is_blank and previous_blank:
            continue

        cleaned_lines.append(line)

        previous_blank = is_blank

    return "\n".join(
        cleaned_lines
    ).strip()


def normalize_soft_hyphen(text: str) -> str:
    """
    Remove Unicode soft-hyphen characters.

    PDF extraction can occasionally contain invisible
    soft-hyphen characters.
    """

    return text.replace(
        "\u00ad",
        "",
    )


def normalize_broken_words(text: str) -> str:
    """
    Repair words broken by PDF line wrapping.

    Example
    -------
        Enginee-
        ring

    becomes:

        Engineering

    while preserving normal hyphenated words such as:

        E-Mail
        Web-basierte

    The rule only joins a hyphen when the hyphen occurs
    immediately before a newline and is followed by a
    lowercase/uppercase alphabetic character.
    """

    # Handle hyphen + newline + word continuation.

    text = re.sub(
        r"(?<=[A-Za-zÄÖÜäöüß])-\n(?=[A-Za-zÄÖÜäöüß])",
        "",
        text,
    )

    return text


def normalize_text(text: str) -> str:
    """
    Apply all basic text normalization operations.
    """

    if not text:
        return ""

    text = normalize_soft_hyphen(
        text
    )

    text = normalize_broken_words(
        text
    )

    text = normalize_whitespace(
        text
    )

    return text


# ============================================================
# PAGE NUMBER DETECTION
# ============================================================

def is_page_number_block(
    text: str,
) -> bool:
    """
    Determine whether a block contains only a standalone
    page number.

    Examples
    --------
        "12"
        "12 "
        " 12 "

    are considered page-number candidates.

    More complicated content such as:

        "Nr. 48/2025"

    is NOT classified as a page number.
    """

    text = text.strip()

    if not text:
        return False

    return bool(
        re.fullmatch(
            r"\d{1,4}",
            text,
        )
    )


# ============================================================
# BLOCK TEXT EXTRACTION
# ============================================================

def extract_block_text(
    block: dict[str, Any],
) -> str:
    """
    Reconstruct block text from its extracted lines and spans.

    The raw extractor already provides lines and spans.
    We use the span text rather than relying on a separate
    PDF extraction pass.
    """

    lines = block.get(
        "lines",
        [],
    )

    reconstructed_lines = []

    for line in lines:

        spans = line.get(
            "spans",
            [],
        )

        line_text = "".join(
            span.get(
                "text",
                "",
            )
            for span in spans
        )

        reconstructed_lines.append(
            line_text
        )

    return "\n".join(
        reconstructed_lines
    )


# ============================================================
# BLOCK CLEANING
# ============================================================

def clean_block(
    block: dict[str, Any],
    page: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Clean one raw extraction block.

    Returns
    -------
    dict
        Cleaned block.

    None
        If the block should be discarded.
    """

    raw_text = extract_block_text(
        block
    )

    text = normalize_text(
        raw_text
    )

    # --------------------------------------------------------
    # REMOVE EMPTY BLOCKS
    # --------------------------------------------------------

    if not text:
        return None

    # --------------------------------------------------------
    # DETERMINE ROLE
    # --------------------------------------------------------

    if is_page_number_block(
        text
    ):
        role = "page_number"
    else:
        role = "text"

    # --------------------------------------------------------
    # BUILD CLEAN BLOCK
    # --------------------------------------------------------

    return {
        "block_index": block.get(
            "block_index"
        ),

        "page_index": page.get(
            "page_index"
        ),

        "page_number": page.get(
            "page_number"
        ),

        "bbox": block.get(
            "bbox"
        ),

        "role": role,

        "text": text,

        # Keep references to the raw structure.
        #
        # This is useful later for debugging and provenance.

        "source": {
            "block_index": block.get(
                "block_index"
            ),
        },
    }


# ============================================================
# PAGE CLEANING
# ============================================================

def clean_page(
    page: dict[str, Any],
) -> dict[str, Any]:
    """
    Clean all blocks belonging to one PDF page.
    """

    cleaned_blocks = []

    blocks = page.get(
        "blocks",
        [],
    )

    for block in blocks:

        # PyMuPDF text blocks use type 0.
        #
        # Ignore image/vector blocks at this stage.

        if block.get(
            "type"
        ) != 0:

            continue

        cleaned = clean_block(
            block=block,
            page=page,
        )

        if cleaned is None:
            continue

        cleaned_blocks.append(
            cleaned
        )

    return {
        "page_index": page.get(
            "page_index"
        ),

        "page_number": page.get(
            "page_number"
        ),

        "width": page.get(
            "width"
        ),

        "height": page.get(
            "height"
        ),

        "blocks": cleaned_blocks,
    }


# ============================================================
# DOCUMENT CLEANING
# ============================================================

def clean_document(
    extraction: dict[str, Any] | list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Clean the complete extracted document.

    Supports both:

        {
            "pages": [...]
        }

    and:

        [...]
    
    depending on how the extraction JSON is structured.
    """

    # --------------------------------------------------------
    # SUPPORT BOTH POSSIBLE ROOT STRUCTURES
    # --------------------------------------------------------

    if isinstance(
        extraction,
        dict,
    ):

        pages = extraction.get(
            "pages",
            [],
        )

    elif isinstance(
        extraction,
        list,
    ):

        pages = extraction

    else:

        raise TypeError(
            "Extraction must be a dictionary or list."
        )

    # --------------------------------------------------------
    # CLEAN PAGES
    # --------------------------------------------------------

    cleaned_pages = []

    for page in pages:

        cleaned_page = clean_page(
            page
        )

        cleaned_pages.append(
            cleaned_page
        )

    # --------------------------------------------------------
    # RETURN CLEANED DOCUMENT
    # --------------------------------------------------------

    return {
        "pages": cleaned_pages
    }


# ============================================================
# FILE HELPERS
# ============================================================

def load_extraction(
    input_path: Path,
) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Load raw extraction JSON from disk.
    """

    import json

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


def save_cleaned_document(
    document: dict[str, Any],
    output_path: Path,
) -> None:
    """
    Save the cleaned document as JSON.
    """

    import json

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            document,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# PIPELINE ENTRY FUNCTION
# ============================================================

def clean_extraction_file(
    input_path: Path,
    output_path: Path,
) -> None:
    """
    Complete file-based cleaning operation.

    raw extraction JSON
            ↓
        load JSON
            ↓
        clean document
            ↓
        save cleaned JSON
    """

    extraction = load_extraction(
        input_path
    )

    cleaned = clean_document(
        extraction
    )

    save_cleaned_document(
        document=cleaned,
        output_path=output_path,
    )