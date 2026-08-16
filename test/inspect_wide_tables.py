"""
Inspect wide tables in the TU Chemnitz Web Engineering
2025 Study Regulation.

Wide tables are tables containing more than two columns.
They are likely to represent study plans, module overviews,
semester structures, or similar tabular information.

This script is for investigation only.
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


# ============================================================
# TABLE INSPECTION
# ============================================================

def inspect_wide_tables(pdf_path: Path) -> None:
    """
    Find and display all tables containing more than
    two columns.
    """

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = fitz.open(pdf_path)

    wide_table_count = 0

    try:

        for page_index, page in enumerate(document):

            page_number = page_index + 1

            tables = page.find_tables().tables

            if not tables:
                continue

            for table_index, table in enumerate(tables):

                extracted = table.extract()

                if not extracted:
                    continue

                column_count = max(
                    len(row)
                    for row in extracted
                )

                # ------------------------------------------------
                # ONLY INSPECT TABLES WITH > 2 COLUMNS
                # ------------------------------------------------

                if column_count <= 2:
                    continue

                wide_table_count += 1

                print()
                print("=" * 80)
                print(
                    f"PAGE {page_number} | "
                    f"TABLE {table_index + 1}"
                )
                print("=" * 80)

                print(
                    f"Rows: {len(extracted)}"
                )

                print(
                    f"Columns: {column_count}"
                )

                print(
                    f"Bounding box: {table.bbox}"
                )

                # ------------------------------------------------
                # PRINT TABLE
                # ------------------------------------------------

                print()
                print("TABLE CONTENT")
                print("-" * 80)

                for row_index, row in enumerate(
                    extracted
                ):

                    print(
                        f"\nRow {row_index + 1}:"
                    )

                    for column_index, cell in enumerate(
                        row
                    ):

                        if cell is None:

                            value = "<None>"

                        else:

                            value = (
                                str(cell)
                                .replace(
                                    "\n",
                                    " "
                                )
                                .strip()
                            )

                        if len(value) > 250:

                            value = (
                                value[:250]
                                + "..."
                            )

                        print(
                            f"  C{column_index + 1}: "
                            f"{value!r}"
                        )

        # ====================================================
        # SUMMARY
        # ====================================================

        print()
        print("=" * 80)
        print("WIDE TABLE SUMMARY")
        print("=" * 80)

        print(
            f"Wide tables detected: "
            f"{wide_table_count}"
        )

    finally:

        document.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    inspect_wide_tables(
        pdf_path=PDF_PATH
    )