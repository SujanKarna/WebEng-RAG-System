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



from src.etl.parser.module_description.module_description_parser import (
    merge_module_blocks,
    parse_module_descriptions,
)
from src.etl.parser.module_description.module_description_validator import (
    print_validation_report,
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

    # ============================================================
    # MODULE DESCRIPTION PARSING TEST
    # ============================================================

    from src.etl.parser.module_description.module_description_parser import (
        merge_module_blocks,
        parse_module_descriptions,
    )

    print("\n" + "=" * 80)
    print("MODULE DESCRIPTION PARSING")
    print("=" * 80)

    # ------------------------------------------------------------
    # 1. Merge module blocks
    # ------------------------------------------------------------

    merged_modules = merge_module_blocks(cleaned_blocks)

    print(
        f"Merged module descriptions: {len(merged_modules)}"
    )

    # ------------------------------------------------------------
    # 2. Parse module descriptions
    # ------------------------------------------------------------

    module_descriptions = parse_module_descriptions(
        merged_modules
    )

    print(
        f"Parsed module descriptions: "
        f"{len(module_descriptions)}"
    )

    # ------------------------------------------------------------
    # 3. Inspect parsed modules
    # ------------------------------------------------------------

    from src.etl.parser.module_description.module_description_validator import (
    print_validation_report,
    )

    modules = parse_module_descriptions(
    merged_modules
    )

    print(
        f"Parsed module descriptions: {len(modules)}"
    )

    print_validation_report(
        modules
    )

if __name__ == "__main__":
    main()

