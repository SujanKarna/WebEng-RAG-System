from src.config.settings import (
    WEB_ENGINEERING_2025_PATH,
    RAW_EXTRACTION_PATH,
    TOC_PATH,
)

from src.etl.extract.pdf_extractor import (
    extract_pdf,
    save_extraction,
)

from src.etl.parser.zone_detector import (
    detect_zones,
)

from src.etl.parser.toc.toc_processor import (
    process_toc,
    save_toc,
)


def main():

    # ========================================================
    # 1. PDF EXTRACTION
    # ========================================================

    print("=" * 80)
    print("1. PDF EXTRACTION")
    print("=" * 80)

    pages = extract_pdf(
        WEB_ENGINEERING_2025_PATH
    )

    save_extraction(
        pages,
        RAW_EXTRACTION_PATH,
    )

    print(
        f"Extracted {len(pages)} pages."
    )

    print(
        f"Saved to: {RAW_EXTRACTION_PATH}"
    )


    # ========================================================
    # 2. ZONE DETECTION
    # ========================================================

    print()
    print("=" * 80)
    print("2. ZONE DETECTION")
    print("=" * 80)

    pages = detect_zones(
        pages
    )

    print(
        "Document zones assigned."
    )


    # ========================================================
    # 3. TOC EXTRACTION
    # ========================================================

    print()
    print("=" * 80)
    print("3. TOC EXTRACTION")
    print("=" * 80)

    toc = process_toc(
        pages
    )

    save_toc(
        toc,
        TOC_PATH,
    )

    print(
        f"TOC saved to: {TOC_PATH}"
    )

    # --------------------------------------------------------
    # Display parsed TOC
    # --------------------------------------------------------

    for part in toc["parts"]:

        print(
            f"\n{part['part']}: "
            f"{part['title']}"
        )

        for regulation in part[
            "regulations"
        ]:

            print(
                f"  {regulation['paragraph']} "
                f"{regulation['title']}"
            )


    # ========================================================
    # 4. CLEANING
    # ========================================================

    print()
    print("=" * 80)
    print("4. CLEANING")
    print("=" * 80)

    # --------------------------------------------------------
    # We will add this next.
    #
    # cleaned = clean_document(pages)
    #
    # save_cleaned(
    #     cleaned,
    #     CLEANED_EXTRACTION_PATH,
    # )
    # --------------------------------------------------------

    print(
        "Cleaning stage not implemented yet."
    )


    # ========================================================
    # PIPELINE COMPLETE
    # ========================================================

    print()
    print("=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()