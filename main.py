from src.config.settings import (
    WEB_ENGINEERING_2025_PATH,
    RAW_EXTRACTION_PATH,
    TOC_PATH,
    PARSED_MAIN_REGULATION_PATH,
    NORMALIZED_MAIN_REGULATION_PATH,
    PARSED_MODULE_DESCRIPTIONS_PATH,
    NORMALIZED_MODULE_DESCRIPTIONS_PATH,
)


# ============================================================
# EXTRACTION
# ============================================================

from src.etl.extract.pdf_extractor import (
    extract_pdf,
    save_extraction,
)


# ============================================================
# PARSING
# ============================================================

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
    RegulationParser,
)

from src.etl.parser.module_description.module_description_parser import (
    merge_module_blocks,
    parse_module_descriptions,
)


# ============================================================
# VALIDATION
# ============================================================

from src.etl.parser.regulation.main_regulation_normalizer_validator import (
    print_normalized_main_regulation_validation_report,
)

from src.etl.parser.module_description.module_description_normalizer_validator import (
    print_normalized_validation_report,
)



# ============================================================
# NORMALIZATION
# ============================================================

from src.etl.parser.regulation.main_regulation_normalizer import (
    MainRegulationNormalizer,
)

from src.etl.parser.module_description.module_description_normalizer import (
    normalize_modules,
)


# ============================================================
# VALIDATION
# ============================================================

from src.etl.parser.module_description.module_description_normalizer_validator import (
    print_normalized_validation_report,
)


# ============================================================
# PERSISTENCE
# ============================================================

from src.etl.persistence.regulation_writer import (
    RegulationWriter,
)

from src.etl.persistence.normalized_main_regulation_writer import (
    NormalizedMainRegulationWriter,
)

from src.etl.persistence.module_description_writer import (
    ModuleDescriptionWriter,
)

# ============================================================
# VALIDATOR
# ============================================================

from src.etl.validator.cross_document_validator import (
    print_cross_document_validation_report,
)


def main():

    # ========================================================
    # 1. PDF EXTRACTION
    # ========================================================

    print("\n" + "=" * 80)
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
        "PDF extraction complete."
    )


    # ========================================================
    # 2. ZONE DETECTION
    # ========================================================

    print("\n" + "=" * 80)
    print("2. ZONE DETECTION")
    print("=" * 80)

    pages = detect_zones(
        pages
    )

    print(
        "Zone detection complete."
    )


    # ========================================================
    # 3. TOC EXTRACTION
    # ========================================================

    print("\n" + "=" * 80)
    print("3. TOC EXTRACTION")
    print("=" * 80)

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

    print("\n" + "=" * 80)
    print("4. CLEANING")
    print("=" * 80)

    cleaned_blocks = clean_blocks(
        pages
    )

    print(
        f"Cleaning complete: "
        f"{len(cleaned_blocks)} blocks"
    )


    # ========================================================
    # 5. MAIN REGULATION
    # ========================================================

    print("\n" + "=" * 80)
    print("5. MAIN REGULATION")
    print("=" * 80)

    regulation_parser = RegulationParser(
        blocks=cleaned_blocks
    )

    main_regulation = (
        regulation_parser.parse()
    )

    print(
        f"Main regulation paragraphs: "
        f"{len(main_regulation)}"
    )


    # --------------------------------------------------------
    # Persist parsed main regulation
    # --------------------------------------------------------

    main_regulation_writer = RegulationWriter(
        PARSED_MAIN_REGULATION_PATH
    )

    main_regulation_writer.write(
        main_regulation
    )

    print(
        "Parsed main regulation persisted."
    )


    # ========================================================
    # 6. NORMALIZE MAIN REGULATION
    # ========================================================

    print("\n" + "=" * 80)
    print("6. NORMALIZE MAIN REGULATION")
    print("=" * 80)

    main_regulation_normalizer = (
        MainRegulationNormalizer()
    )

    normalized_main_regulation = (
        main_regulation_normalizer.normalize(
            main_regulation
        )
    )

    print(
        f"Normalized main regulation paragraphs: "
        f"{len(normalized_main_regulation)}"
    )

    print_normalized_main_regulation_validation_report(
    normalized_main_regulation
    )


    # --------------------------------------------------------
    # Persist normalized main regulation
    # --------------------------------------------------------

    normalized_main_regulation_writer = (
        NormalizedMainRegulationWriter(
            NORMALIZED_MAIN_REGULATION_PATH
        )
    )

    normalized_main_regulation_writer.write(
        normalized_main_regulation
    )

    print(
        "Normalized main regulation persisted."
    )

    print(
        f"  {NORMALIZED_MAIN_REGULATION_PATH}"
    )


    # ========================================================
    # 7. MODULE DESCRIPTIONS
    # ========================================================

    print("\n" + "=" * 80)
    print("7. MODULE DESCRIPTIONS")
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

    module_descriptions = (
        parse_module_descriptions(
            merged_modules
        )
    )

    print(
        f"Parsed module descriptions: "
        f"{len(module_descriptions)}"
    )


    # --------------------------------------------------------
    # Persist parsed module descriptions
    # --------------------------------------------------------

    module_writer = ModuleDescriptionWriter(
        PARSED_MODULE_DESCRIPTIONS_PATH
    )

    module_writer.write(
        module_descriptions
    )

    print(
        "Parsed module descriptions persisted."
    )


    # ========================================================
    # 8. NORMALIZE MODULE DESCRIPTIONS
    # ========================================================

    print("\n" + "=" * 80)
    print("8. NORMALIZE MODULE DESCRIPTIONS")
    print("=" * 80)

    normalized_modules = normalize_modules(
        module_descriptions
    )

    print(
        f"Normalized module descriptions: "
        f"{len(normalized_modules)}"
    )


    # --------------------------------------------------------
    # Persist normalized module descriptions
    # --------------------------------------------------------

    normalized_module_writer = (
        ModuleDescriptionWriter(
            NORMALIZED_MODULE_DESCRIPTIONS_PATH
        )
    )

    normalized_module_writer.write(
        normalized_modules
    )

    print(
        "Normalized module descriptions persisted."
    )

    print(
        f"  {NORMALIZED_MODULE_DESCRIPTIONS_PATH}"
    )


    # ========================================================
    # 9. VALIDATE MODULE DESCRIPTIONS
    # ========================================================

    print("\n" + "=" * 80)
    print("9. MODULE DESCRIPTION VALIDATION")
    print("=" * 80)

    print_normalized_validation_report(
        normalized_modules
    )

    # ========================================================
    # 10. CROSS-DOCUMENT VALIDATION
    # ========================================================

    print("\n" + "=" * 80)
    print("10. CROSS-DOCUMENT VALIDATION")
    print("=" * 80)

    print_cross_document_validation_report(
        NORMALIZED_MAIN_REGULATION_PATH,
        NORMALIZED_MODULE_DESCRIPTIONS_PATH,
    )

    # ========================================================
    # PIPELINE COMPLETE
    # ========================================================

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()