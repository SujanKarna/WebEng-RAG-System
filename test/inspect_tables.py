"""
Table inspection utility for the TU Chemnitz Web Engineering
2025 Study Regulation.

Purpose
-------
This script is used only for investigating how PyMuPDF
detects and extracts tables from the source PDF.

It does NOT:
    - modify the PDF
    - modify the raw extraction JSON
    - perform cleaning
    - perform chunking
    - classify tables
    - modify the ETL pipeline

The output helps us understand the different table structures
present in the study regulation before implementing the actual
table-processing stage.
"""

from pathlib import Path

import fitz


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "tu_chemnitz_web_engineering_2025.pdf"
)

# Number of rows to display from each table.
SAMPLE_ROWS = 3


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_table_dimensions(
    extracted_table: list[list[str | None]],
) -> tuple[int, int]:
    """
    Determine the dimensions of an extracted table.

    We calculate the dimensions from table.extract()
    instead of relying on table.rows or table.columns,
    because the PyMuPDF Table API differs between versions.
    """

    if not extracted_table:
        return 0, 0

    row_count = len(extracted_table)

    column_count = max(
        len(row)
        for row in extracted_table
    )

    return row_count, column_count


def print_table_sample(
    extracted_table: list[list[str | None]],
    sample_rows: int = SAMPLE_ROWS,
) -> None:
    """
    Print a limited sample of the extracted table.

    Long cell contents are truncated so that the terminal
    remains readable.
    """

    print()
    print("Sample data:")
    print("-" * 50)

    for row_index, row in enumerate(
        extracted_table[:sample_rows]
    ):

        print(
            f"Row {row_index + 1}:"
        )

        for column_index, cell in enumerate(row):

            if cell is None:

                display_value = "<None>"

            else:

                display_value = (
                    str(cell)
                    .replace("\n", " ")
                    .strip()
                )

            # Keep the terminal output manageable.

            if len(display_value) > 150:

                display_value = (
                    display_value[:150]
                    + "..."
                )

            print(
                f"  [{column_index + 1}] "
                f"{display_value!r}"
            )


# ============================================================
# TABLE INSPECTION
# ============================================================

def inspect_tables(pdf_path: Path) -> None:
    """
    Scan the complete PDF and inspect detected tables.

    The function produces:

    1. A compact inventory of detected tables.
    2. A small sample of each table.
    3. A distribution of table dimensions.
    """

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if not pdf_path.is_file():

        raise FileNotFoundError(
            f"Path is not a file: {pdf_path}"
        )

    # --------------------------------------------------------
    # OPEN PDF
    # --------------------------------------------------------

    print("=" * 70)
    print("TABLE INSPECTION")
    print("=" * 70)

    print(
        f"PDF: {pdf_path}"
    )

    print()

    document = fitz.open(pdf_path)

    # Capture page count BEFORE closing the document.
    total_pages = document.page_count

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_tables = 0

    pages_with_tables = 0

    tables_by_dimensions = {}

    # ========================================================
    # PROCESS EACH PAGE
    # ========================================================

    try:

        for page_index, page in enumerate(document):

            page_number = page_index + 1

            # ------------------------------------------------
            # DETECT TABLES
            # ------------------------------------------------

            table_finder = page.find_tables()

            tables = table_finder.tables

            # No tables on this page.
            if not tables:
                continue

            pages_with_tables += 1

            print()
            print("=" * 70)
            print(
                f"PAGE {page_number}"
            )
            print("=" * 70)

            print(
                f"Tables detected: {len(tables)}"
            )

            # ------------------------------------------------
            # PROCESS EACH TABLE
            # ------------------------------------------------

            for table_index, table in enumerate(tables):

                total_tables += 1

                # --------------------------------------------
                # EXTRACT TABLE
                # --------------------------------------------

                extracted = table.extract()

                # --------------------------------------------
                # DETERMINE DIMENSIONS
                # --------------------------------------------

                row_count, column_count = (
                    get_table_dimensions(
                        extracted
                    )
                )

                # --------------------------------------------
                # UPDATE STATISTICS
                # --------------------------------------------

                dimension_key = (
                    row_count,
                    column_count,
                )

                tables_by_dimensions[
                    dimension_key
                ] = (
                    tables_by_dimensions.get(
                        dimension_key,
                        0,
                    )
                    + 1
                )

                # --------------------------------------------
                # TABLE INFORMATION
                # --------------------------------------------

                print()
                print(
                    "-" * 70
                )

                print(
                    f"TABLE {table_index + 1}"
                )

                print(
                    f"Dimensions: "
                    f"{row_count} rows × "
                    f"{column_count} columns"
                )

                print(
                    f"Bounding box: "
                    f"{table.bbox}"
                )

                # --------------------------------------------
                # SAMPLE DATA
                # --------------------------------------------

                print_table_sample(
                    extracted_table=extracted,
                    sample_rows=SAMPLE_ROWS,
                )

    finally:

        document.close()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print()
    print("=" * 70)
    print("TABLE INSPECTION SUMMARY")
    print("=" * 70)

    # Use the captured value instead of accessing the
    # already-closed PyMuPDF document.

    print(
        f"PDF pages: {total_pages}"
    )

    print(
        f"Pages containing tables: "
        f"{pages_with_tables}"
    )

    print(
        f"Total tables detected: "
        f"{total_tables}"
    )

    # --------------------------------------------------------
    # TABLE DIMENSION DISTRIBUTION
    # --------------------------------------------------------

    print()
    print(
        "TABLE DIMENSION DISTRIBUTION"
    )

    print("-" * 50)

    if not tables_by_dimensions:

        print(
            "No tables were detected."
        )

    else:

        sorted_dimensions = sorted(
            tables_by_dimensions.items()
        )

        for (
            (rows, columns),
            count,
        ) in sorted_dimensions:

            print(
                f"{rows:>3} rows × "
                f"{columns:<3} columns"
                f"  →  {count} table(s)"
            )

    print()
    print("=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    inspect_tables(
        pdf_path=PDF_PATH
    )