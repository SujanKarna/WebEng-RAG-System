from pathlib import Path
import pymupdf
import json

class PDFExtractionError(Exception):
    """Raised when PDF extraction fails."""
    pass


def extract_pdf(pdf_path: Path) -> list[dict]:
    """
    Extract raw PDF structure.

    Parameters
    ----------
    pdf_path:
        Path to the PDF document.

    Returns
    -------
    list[dict]
        A list containing the extracted information for
        every page.

    Raises
    ------
    PDFExtractionError
        If the PDF cannot be opened or extracted.
    """

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not pdf_path.exists():
        raise PDFExtractionError(
            f"PDF file does not exist: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise PDFExtractionError(
            f"Path is not a file: {pdf_path}"
        )

    # --------------------------------------------------------
    # OPEN PDF
    # --------------------------------------------------------

    try:
        document = pymupdf.open(pdf_path)

    except Exception as exc:
        raise PDFExtractionError(
            f"Unable to open PDF: {pdf_path}"
        ) from exc

    pages = []

    try:

        # ----------------------------------------------------
        # PROCESS EACH PAGE
        # ----------------------------------------------------

        for page_index, page in enumerate(document):

            # ------------------------------------------------
            # PAGE INFORMATION
            # ------------------------------------------------

            page_rect = page.rect

            page_data = {
                "page_index": page_index,
                "page_number": page_index + 1,
                "width": page_rect.width,
                "height": page_rect.height,
                "blocks": [],
            }

            # ------------------------------------------------
            # EXTRACT BLOCKS
            # ------------------------------------------------

            blocks = page.get_text(
                "dict"
            ).get("blocks", [])

            for block_index, block in enumerate(blocks):

                block_data = {
                    "block_index": block_index,
                    "type": block.get("type"),
                    "bbox": block.get("bbox"),
                    "lines": [],
                }

                # --------------------------------------------
                # EXTRACT LINES
                # --------------------------------------------

                for line_index, line in enumerate(
                    block.get("lines", [])
                ):

                    line_data = {
                        "line_index": line_index,
                        "bbox": line.get("bbox"),
                        "wmode": line.get("wmode"),
                        "dir": line.get("dir"),
                        "spans": [],
                    }

                    # ----------------------------------------
                    # EXTRACT SPANS
                    # ----------------------------------------

                    for span_index, span in enumerate(
                        line.get("spans", [])
                    ):

                        span_data = {
                            "span_index": span_index,
                            "text": span.get("text", ""),
                            "bbox": span.get("bbox"),
                            "origin": span.get("origin"),
                            "font": span.get("font"),
                            "size": span.get("size"),
                            "flags": span.get("flags"),
                            "color": span.get("color"),
                            "ascender": span.get("ascender"),
                            "descender": span.get("descender"),
                        }

                        line_data["spans"].append(
                            span_data
                        )

                    block_data["lines"].append(
                        line_data
                    )

                page_data["blocks"].append(
                    block_data
                )

            pages.append(page_data)

    except Exception as exc:

        raise PDFExtractionError(
            f"Failed while extracting PDF: {pdf_path}"
        ) from exc

    finally:
        document.close()

    return pages



def save_extraction(
    pages: list[dict],
    output_path: Path,
) -> None:
    """
    Save the raw PDF extraction as JSON.

    The extracted representation is intentionally stored
    before any cleaning or structural interpretation.
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
            pages,
            file,
            indent=2,
            ensure_ascii=False,
        )