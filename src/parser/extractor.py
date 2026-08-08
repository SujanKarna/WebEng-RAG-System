import fitz

from src.models.block import Block


def extract(pdf_path: str) -> list[Block]:
    """
    Extract raw PDF text blocks.

    Responsibility:
        PDF -> list[Block]

    Does NOT:
        - detect headings
        - detect sections
        - detect tables
        - parse document structure
        - use regex
    """

    document = fitz.open(pdf_path)

    blocks = []

    for page_number, page in enumerate(document, start=1):

        page_dict = page.get_text("dict")

        for block in page_dict["blocks"]:

            # Ignore images/non-text blocks
            if "lines" not in block:
                continue

            text_parts = []

            font_sizes = []
            font_names = []
            bold_flags = []

            raw_spans = []

            for line in block["lines"]:

                for span in line["spans"]:

                    raw_spans.append(span)

                    text_parts.append(span["text"])

                    font_sizes.append(span["size"])

                    font_names.append(span["font"])

                    bold_flags.append(
                        "bold" in span["font"].lower()
                        or "black" in span["font"].lower()
                    )

            text = "".join(text_parts).strip()

            # Ignore empty text blocks
            if not text:
                continue

            bbox = block["bbox"]

            blocks.append(
                Block(
                    pdf_page=page_number,

                    text=text,

                    x0=bbox[0],
                    y0=bbox[1],
                    x1=bbox[2],
                    y1=bbox[3],

                    font_size=max(font_sizes)
                    if font_sizes
                    else 0,

                    font_name=font_names[0]
                    if font_names
                    else "",

                    is_bold=any(bold_flags),

                    spans=raw_spans
                )
            )

    document.close()

    return blocks