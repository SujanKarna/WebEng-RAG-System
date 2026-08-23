from src.config.settings import (
    WEB_ENGINEERING_2025_PATH,
    RAW_EXTRACTION_PATH,
    TOC_PATH,
    REGULATION_STRUCTURE_PATH,
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

from src.etl.parser.module_description.module_description_normalizer import (
    normalize_modules,
)

from src.etl.parser.regulation.module_description_index import (
    build_module_description_index,
)

'''from src.etl.parser.module_description.module_description_validator import (
    print_validation_report,
)'''

from src.etl.parser.module_description.module_description_normalizer_validator import (
    print_normalized_validation_report,
)

from src.etl.parser.regulation.regulation_parser import (
    structure_regulations,
)

from src.etl.persistence.regulation_writer import (
    save_regulation_structure,
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
    # 5. MODULE DESCRIPTION PARSING
    # ========================================================

    print("\n" + "=" * 80)
    print("MODULE DESCRIPTION PARSING")
    print("=" * 80)

    # --------------------------------------------------------
    # Merge module description blocks
    # --------------------------------------------------------

    merged_modules = merge_module_blocks(
        cleaned_blocks
    )

    print(
        f"Merged module descriptions: "
        f"{len(merged_modules)}"
    )

    # --------------------------------------------------------
    # Parse module descriptions
    # --------------------------------------------------------

    module_descriptions = parse_module_descriptions(
        merged_modules
    )

    print(
        f"Parsed module descriptions: "
        f"{len(module_descriptions)}"
    )

    # --------------------------------------------------------
    # Normalize module descriptions
    # --------------------------------------------------------

    normalized_modules = normalize_modules(
        module_descriptions
    )

    print(
        f"Normalized module descriptions: "
        f"{len(normalized_modules)}"
    )

    # --------------------------------------------------------
    # Validate normalized modules
    # --------------------------------------------------------

    print_normalized_validation_report(
        normalized_modules
    )

    # --------------------------------------------------------
    # Build module description index
    # --------------------------------------------------------

    module_description_index = (
        build_module_description_index(
            normalized_modules
        )
    )

    print(
        f"Module description index: "
        f"{len(module_description_index)}"
    )

    # --------------------------------------------------------
    # Test module lookup
    # --------------------------------------------------------

    test_code = "261032-210"

    description = module_description_index.get(
        test_code
    )

    if description:

        print(
            f"Found: "
            f"{description.module_code} "
            f"-> "
            f"{description.module_name}"
        )

    else:

        print(
            f"Not found: "
            f"{test_code}"
        )

    # ========================================================
    # 6. REGULATION STRUCTURING
    # ========================================================

    print("\n" + "=" * 80)
    print("REGULATION STRUCTURING")
    print("=" * 80)

    regulations = structure_regulations(
    blocks=cleaned_blocks,
    toc=toc,
    module_description_index=module_description_index,
    )


    # ========================================================
    # 7. PERSIST REGULATION STRUCTURE
    # ========================================================

    save_regulation_structure(
        regulation=regulations,
        output_path=REGULATION_STRUCTURE_PATH,
    )

    print(
        "Regulation structure persisted."
    )

if __name__ == "__main__":
    main()