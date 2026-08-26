from src.config.settings import (
    WEB_ENGINEERING_2025_PATH,
    RAW_EXTRACTION_PATH,
    TOC_PATH,
    PARSED_MAIN_REGULATION_PATH,
    NORMALIZED_MAIN_REGULATION_PATH,
    PARSED_MODULE_DESCRIPTIONS_PATH,
    NORMALIZED_MODULE_DESCRIPTIONS_PATH,
    CHUNKS_PATH,
    EMBEDDINGS_PATH
)

import numpy as np
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
# CHUNKER
# ============================================================
from src.chunking.chunk_writer import (
    ChunkWriter,
)
from src.chunking.module_chunker import (
    chunk_module_descriptions,
)

from src.chunking.regulation_chunker import (
    chunk_main_regulation,
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
    # 11. MODULE CHUNKING
    # ========================================================

    print("\n" + "=" * 80)
    print("11. MODULE CHUNKING")
    print("=" * 80)

    # --------------------------------------------------------
    # Load authoritative persisted normalized data
    # --------------------------------------------------------

    import json

    with open(
        NORMALIZED_MAIN_REGULATION_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        persisted_main_regulation = json.load(
            file
        )

    with open(
        NORMALIZED_MODULE_DESCRIPTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        persisted_modules = json.load(
            file
        )

    print(
        f"Loaded persisted main regulation: "
        f"{len(persisted_main_regulation)} paragraphs"
    )

    print(
        f"Loaded persisted module descriptions: "
        f"{len(persisted_modules)} modules"
    )

    # --------------------------------------------------------
    # Build regulation chunks
    # --------------------------------------------------------

    regulation_chunks = chunk_main_regulation(
        regulation=persisted_main_regulation,
    )

    print(
        f"Created regulation chunks: "
        f"{len(regulation_chunks)}"
    )

    # --------------------------------------------------------
    # Build module chunks
    # --------------------------------------------------------

    module_chunks = chunk_module_descriptions(
        modules=persisted_modules,
        regulation=persisted_main_regulation,
    )

    print(
        f"Created module chunks: "
        f"{len(module_chunks)}"
    )

    # --------------------------------------------------------
    # Combine chunks
    # --------------------------------------------------------

    chunks = (
        regulation_chunks
        + module_chunks
    )

    # Re-index chunks globally
    for index, chunk in enumerate(chunks):
        chunk.chunk_index = index

    print(
        f"Total chunks: {len(chunks)}"
    )

    # --------------------------------------------------------
    # Persist all chunks
    # --------------------------------------------------------

    chunk_writer = ChunkWriter(
        CHUNKS_PATH
    )

    chunk_writer.write(
        chunks
    )

    print(
        "All chunks persisted."
    )

    print(
        f"  {CHUNKS_PATH}"
    )


    # ========================================================
    # 12. VALIDATE PERSISTED CHUNKS
    # ========================================================

    print("\n" + "=" * 80)
    print("12. VALIDATE PERSISTED CHUNKS")
    print("=" * 80)

    from src.chunking.chunk_validator import ChunkValidator

    validator = ChunkValidator(
        CHUNKS_PATH
    )

    chunks = validator.load()

    validator.summary(
        chunks
    )

    validator.validate()


    # ========================================================
    # 13. EMBEDDING
    # ========================================================

    print("\n" + "=" * 80)
    print("13. EMBEDDING")
    print("=" * 80)

    import json

    from src.embedding.embedder import BGEEmbedder
    from src.embedding.embedding_writer import EmbeddingWriter


    # --------------------------------------------------------
    # Load authoritative persisted chunks
    # --------------------------------------------------------

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        persisted_chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]


    print(
        f"Loaded chunks: "
        f"{len(persisted_chunks)}"
    )


    # --------------------------------------------------------
    # Build semantic embedding text
    # --------------------------------------------------------

    def build_embedding_text(
        chunk: dict,
    ) -> str:

        context = chunk.get(
            "context",
            {},
        )

        parts = []

        # --------------------------------------------
        # Part
        # --------------------------------------------

        part = context.get(
            "part"
        )

        if part:

            part_name = part.get(
                "part",
                ""
            )

            part_title = part.get(
                "part_title",
                ""
            )

            parts.append(
                f"{part_name}: "
                f"{part_title}".strip()
            )

        # --------------------------------------------
        # Paragraph
        # --------------------------------------------

        paragraph = context.get(
            "paragraph"
        )

        paragraph_title = context.get(
            "paragraph_title"
        )

        if paragraph:

            parts.append(
                f"{paragraph}: "
                f"{paragraph_title or ''}".strip()
            )

        # --------------------------------------------
        # Section
        # --------------------------------------------

        section = context.get(
            "section"
        )

        section_title = context.get(
            "section_title"
        )

        if section:

            parts.append(
                f"Section {section}: "
                f"{section_title or ''}".strip()
            )

        # --------------------------------------------
        # Module
        # --------------------------------------------

        module_code = context.get(
            "module_code"
        )

        module_name = context.get(
            "module_name"
        )

        if module_code:

            parts.append(
                f"Module: "
                f"{module_code} — "
                f"{module_name or ''}".strip()
            )

        # --------------------------------------------
        # Original chunk text
        # --------------------------------------------

        text = chunk.get(
            "text",
            ""
        ).strip()

        if text:
            parts.append(text)

        return "\n\n".join(
            part
            for part in parts
            if part
        )


    embedding_texts = [
        build_embedding_text(chunk)
        for chunk in persisted_chunks
    ]


    print(
        f"Prepared embedding texts: "
        f"{len(embedding_texts)}"
    )


    # --------------------------------------------------------
    # Create embedder
    # --------------------------------------------------------

    embedder = BGEEmbedder()


    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    embeddings = embedder.embed(
        embedding_texts
    )


    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if len(embeddings) != len(
        persisted_chunks
    ):

        raise RuntimeError(
            "Number of embeddings does not "
            "match number of chunks."
        )


    if embeddings.ndim != 2:

        raise RuntimeError(
            "Embeddings must be a 2D matrix."
        )


    dimension = embedder.dimension()


    if embeddings.shape[1] != dimension:

        raise RuntimeError(
            "Embedding dimension mismatch."
        )


    # --------------------------------------------------------
    # Validate values
    # --------------------------------------------------------

    if not np.isfinite(
        embeddings
    ).all():

        raise RuntimeError(
            "Embeddings contain NaN or infinite values."
        )


    # --------------------------------------------------------
    # Persist embedding records
    # --------------------------------------------------------

    embedding_records = []

    for chunk, embedding, embedding_text in zip(
        persisted_chunks,
        embeddings,
        embedding_texts,
    ):

        embedding_records.append(
            {
                "chunk_id": chunk[
                    "chunk_id"
                ],

                "chunk_index": chunk[
                    "chunk_index"
                ],

                "document_id": chunk[
                    "document_id"
                ],

                "chunk_type": chunk[
                    "chunk_type"
                ],

                "text": chunk[
                    "text"
                ],

                "embedding_text": embedding_text,

                "context": chunk.get(
                    "context",
                    {},
                ),

                "page_start": chunk.get(
                    "page_start"
                ),

                "page_end": chunk.get(
                    "page_end"
                ),

                "zone": chunk.get(
                    "zone"
                ),

                "embedding": embedding.tolist(),
            }
        )


    # --------------------------------------------------------
    # Persist
    # --------------------------------------------------------

    embedding_writer = EmbeddingWriter(
        EMBEDDINGS_PATH
    )

    embedding_writer.write(
        embedding_records
    )


    print(
        f"Created embeddings: "
        f"{len(embedding_records)}"
    )

    print(
        f"Embedding dimension: "
        f"{dimension}"
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