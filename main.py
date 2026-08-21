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
    extract_toc,
    save_toc,
)

from src.etl.parser.cleaner import (
    clean_blocks,
)

from src.etl.parser.regulation.regulation_parser import (
    structure_regulations,
)


def main():

    # ========================================================
    # 1. PDF EXTRACTION
    # ========================================================

    pages = extract_pdf(
        WEB_ENGINEERING_2025_PATH
    )

    save_extraction(
        pages,
        RAW_EXTRACTION_PATH,
    )

    print(
        "PDF extraction complete."
    )

    # ========================================================
    # 2. ZONE DETECTION
    # ========================================================

    pages = detect_zones(
        pages
    )

    print(
        "Zone detection complete."
    )

    # ========================================================
    # 3. TOC EXTRACTION
    # ========================================================

    toc = extract_toc(
        pages
    )

    save_toc(
        toc,
        TOC_PATH,
    )

    print(
        "TOC extraction complete."
    )

    # ========================================================
    # 4. CLEANING
    # ========================================================

    cleaned_blocks = clean_blocks(
        pages
    )

    print(
        f"Cleaning complete: "
        f"{len(cleaned_blocks)} blocks"
    )

    # ========================================================
    # 5. MAIN REGULATION STRUCTURE
    # ========================================================

    regulations = structure_regulations(
        blocks=cleaned_blocks,
        toc=toc,
    )

    print(
        "Main regulation parsing complete."
    )

    # ========================================================
    # 6. DEBUG § 6 MODULE STRUCTURE
    # ========================================================

    print()
    print("=" * 80)
    print("§ 6 MODULE STRUCTURE")
    print("=" * 80)

    section_6 = None

    # --------------------------------------------------------
    # Find § 6 inside the already structured regulation
    # --------------------------------------------------------

    for part in regulations["parts"]:

        for regulation in part["regulations"]:

            if regulation["paragraph"] == "§ 6":

                section_6 = regulation
                break

        if section_6 is not None:
            break

    # --------------------------------------------------------
    # § 6 not found
    # --------------------------------------------------------

    if section_6 is None:

        print(
            "ERROR: § 6 was not found."
        )

        return

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    print(
        f"\n§ 6: {section_6['title']}"
    )

    print(
        f"Original blocks: "
        f"{len(section_6['blocks'])}"
    )

    print(
        f"Module sections: "
        f"{len(section_6.get('module_sections', []))}"
    )

    # ========================================================
    # 7. PRINT MODULE SECTIONS
    # ========================================================

    for section in section_6.get(
        "module_sections",
        []
    ):

        print()

        print(
            f"{section['number']}. "
            f"{section['title']}"
        )

        print(
            f"    Blocks: "
            f"{len(section['blocks'])}"
        )

        print(
            f"    Modules: "
            f"{len(section['modules'])}"
        )

        # ----------------------------------------------------
        # Print modules
        # ----------------------------------------------------

        for module in section["modules"]:

            print(
                f"      "
                f"{module['module_code']} | "
                f"{module['module_name']} | "
                f"{module['credits']} LP | "
                f"{module['type']} | "
                f"Page {module['page_number']} | "
                f"Block {module['block_index']}"
            )


if __name__ == "__main__":
    main()
