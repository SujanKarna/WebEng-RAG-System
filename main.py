import json

import numpy as np

from src.config.settings import (
    WEB_ENGINEERING_2025_PATH,
    RAW_EXTRACTION_PATH,
    TOC_PATH,
    PARSED_MAIN_REGULATION_PATH,
    NORMALIZED_MAIN_REGULATION_PATH,
    PARSED_MODULE_DESCRIPTIONS_PATH,
    NORMALIZED_MODULE_DESCRIPTIONS_PATH,
    CHUNKS_PATH,
    EMBEDDINGS_PATH,
    FAISS_INDEX_PATH,
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

from src.etl.parser.regulation.main_regulation_normalizer_validator import (
    print_normalized_main_regulation_validation_report,
)

from src.etl.parser.module_description.module_description_normalizer_validator import (
    print_normalized_validation_report,
)

from src.etl.validator.cross_document_validator import (
    print_cross_document_validation_report,
)

from src.chunking.chunk_validator import (
    ChunkValidator,
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
# CHUNKING
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
# EMBEDDING
# ============================================================

from src.embedding.embedder import (
    BGEEmbedder,
)

from src.embedding.embedding_writer import (
    EmbeddingWriter,
)

from src.retrieval.faiss_index import FAISSIndex
# ============================================================
# HELPERS
# ============================================================

def build_embedding_text(chunk: dict) -> str:
    """
    Build a semantically enriched text representation of a chunk.

    Structural metadata such as paragraph, section, module code,
    and module name is included together with the original chunk
    text before embedding.
    """

    context = chunk.get("context", {})

    parts = []

    # --------------------------------------------------------
    # Part
    # --------------------------------------------------------

    part = context.get("part")

    if part:
        part_name = part.get("part", "")
        part_title = part.get("part_title", "")

        value = f"{part_name}: {part_title}".strip()

        if value:
            parts.append(value)

    # --------------------------------------------------------
    # Paragraph
    # --------------------------------------------------------

    paragraph = context.get("paragraph")
    paragraph_title = context.get("paragraph_title")

    if paragraph:
        value = f"{paragraph}: {paragraph_title or ''}".strip()

        if value:
            parts.append(value)

    # --------------------------------------------------------
    # Section
    # --------------------------------------------------------

    section = context.get("section")
    section_title = context.get("section_title")

    if section:
        value = (
            f"Section {section}: "
            f"{section_title or ''}"
        ).strip()

        if value:
            parts.append(value)

    # --------------------------------------------------------
    # Module
    # --------------------------------------------------------

    module_code = context.get("module_code")
    module_name = context.get("module_name")

    if module_code:
        value = (
            f"Module: "
            f"{module_code} — "
            f"{module_name or ''}"
        ).strip()

        if value:
            parts.append(value)

    # --------------------------------------------------------
    # Original chunk text
    # --------------------------------------------------------

    text = chunk.get("text", "").strip()

    if text:
        parts.append(text)

    return "\n\n".join(parts)


def load_json(path: str):
    """
    Load a JSON file using UTF-8 encoding.
    """

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_jsonl(path: str):
    """
    Load a JSONL file using UTF-8 encoding.
    """

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


# ============================================================
# MAIN PIPELINE
# ============================================================

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

    print("PDF extraction complete.")

    # ========================================================
    # 2. ZONE DETECTION
    # ========================================================

    print("\n" + "=" * 80)
    print("2. ZONE DETECTION")
    print("=" * 80)

    pages = detect_zones(
        pages
    )

    print("Zone detection complete.")

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

    print("TOC extraction complete.")

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

    regulation_writer = RegulationWriter(
        PARSED_MAIN_REGULATION_PATH
    )

    regulation_writer.write(
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

    normalizer = MainRegulationNormalizer()

    normalized_main_regulation = (
        normalizer.normalize(
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

    normalized_regulation_writer = (
        NormalizedMainRegulationWriter(
            NORMALIZED_MAIN_REGULATION_PATH
        )
    )

    normalized_regulation_writer.write(
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

    merged_modules = merge_module_blocks(
        cleaned_blocks
    )

    print(
        f"Merged module descriptions: "
        f"{len(merged_modules)}"
    )

    module_descriptions = (
        parse_module_descriptions(
            merged_modules
        )
    )

    print(
        f"Parsed module descriptions: "
        f"{len(module_descriptions)}"
    )

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
    # 9. MODULE DESCRIPTION VALIDATION
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
    # 11. CHUNKING
    # ========================================================

    print("\n" + "=" * 80)
    print("11. CHUNKING")
    print("=" * 80)

    persisted_main_regulation = load_json(
        NORMALIZED_MAIN_REGULATION_PATH
    )

    persisted_modules = load_json(
        NORMALIZED_MODULE_DESCRIPTIONS_PATH
    )

    print(
        f"Loaded persisted main regulation: "
        f"{len(persisted_main_regulation)} paragraphs"
    )

    print(
        f"Loaded persisted module descriptions: "
        f"{len(persisted_modules)} modules"
    )

    regulation_chunks = chunk_main_regulation(
        regulation=persisted_main_regulation,
    )

    print(
        f"Created regulation chunks: "
        f"{len(regulation_chunks)}"
    )

    module_chunks = chunk_module_descriptions(
        modules=persisted_modules,
        regulation=persisted_main_regulation,
    )

    print(
        f"Created module chunks: "
        f"{len(module_chunks)}"
    )

    chunks = (
        regulation_chunks
        + module_chunks
    )

    # Re-index globally.
    for index, chunk in enumerate(chunks):
        chunk.chunk_index = index

    print(
        f"Total chunks: {len(chunks)}"
    )

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
    # 12. CHUNK VALIDATION
    # ========================================================

    print("\n" + "=" * 80)
    print("12. CHUNK VALIDATION")
    print("=" * 80)

    validator = ChunkValidator(
        CHUNKS_PATH
    )

    persisted_chunks = validator.load()

    validator.summary(
        persisted_chunks
    )

    validator.validate()

    # ========================================================
    # 13. EMBEDDING
    # ========================================================

    print("\n" + "=" * 80)
    print("13. EMBEDDING")
    print("=" * 80)

    print("Loading persisted chunks...")

    persisted_chunks = load_jsonl(
        CHUNKS_PATH
    )

    print(
        f"Loaded chunks: "
        f"{len(persisted_chunks)}"
    )

    # --------------------------------------------------------
    # Build embedding texts
    # --------------------------------------------------------

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
    # Validate embedding count
    # --------------------------------------------------------

    if len(embeddings) != len(
        persisted_chunks
    ):
        raise RuntimeError(
            "Number of embeddings does not "
            "match number of chunks."
        )

    # --------------------------------------------------------
    # Validate embedding shape
    # --------------------------------------------------------

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
    # Validate embedding values
    # --------------------------------------------------------

    if not np.isfinite(
        embeddings
    ).all():

        raise RuntimeError(
            "Embeddings contain NaN "
            "or infinite values."
        )

    # --------------------------------------------------------
    # Build embedding records
    # --------------------------------------------------------

    embedding_records = []

    for (
        chunk,
        embedding,
        embedding_text,
    ) in zip(
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
    # Persist embeddings
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

    print(
        f"Embeddings persisted:"
        f"\n  {EMBEDDINGS_PATH}"
    )


    # ========================================================
    # 14. FAISS INDEX
    # ========================================================

    print("\n" + "=" * 80)
    print("14. FAISS INDEX")
    print("=" * 80)

    # --------------------------------------------------------
    # Create FAISS index
    # --------------------------------------------------------

    faiss_index = FAISSIndex(
        dimension=dimension
    )

    # --------------------------------------------------------
    # Build metadata for FAISS
    # --------------------------------------------------------

    faiss_metadata = []

    for record in embedding_records:

        metadata = {
            "chunk_id": record["chunk_id"],
            "chunk_index": record["chunk_index"],
            "document_id": record["document_id"],
            "chunk_type": record["chunk_type"],
            "text": record["text"],
            "embedding_text": record["embedding_text"],
            "context": record.get(
                "context",
                {},
            ),
            "page_start": record.get(
                "page_start"
            ),
            "page_end": record.get(
                "page_end"
            ),
            "zone": record.get(
                "zone"
            ),
        }

        faiss_metadata.append(
            metadata
        )

    # --------------------------------------------------------
    # Convert embeddings to NumPy array
    # --------------------------------------------------------

    faiss_embeddings = np.asarray(
        [
            record["embedding"]
            for record in embedding_records
        ],
        dtype=np.float32,
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if faiss_embeddings.ndim != 2:

        raise RuntimeError(
            "FAISS embeddings must be a 2D matrix."
        )

    if faiss_embeddings.shape[0] != len(
        faiss_metadata
    ):

        raise RuntimeError(
            "Number of embeddings does not "
            "match number of FAISS metadata records."
        )

    if faiss_embeddings.shape[1] != dimension:

        raise RuntimeError(
            "FAISS embedding dimension mismatch."
        )

    # --------------------------------------------------------
    # Add vectors
    # --------------------------------------------------------

    faiss_index.add(
        embeddings=faiss_embeddings,
        metadata=faiss_metadata,
    )

    print(
        f"FAISS vectors added: "
        f"{faiss_index.index.ntotal}"
    )

    # --------------------------------------------------------
    # Persist FAISS index
    # --------------------------------------------------------

    faiss_index.save(
        str(FAISS_INDEX_PATH)
    )

    print(
        "FAISS index successfully created."
    )

    print(
        f"  {FAISS_INDEX_PATH}"
    )

    # --------------------------------------------------------
    # Validate persisted index
    # --------------------------------------------------------

    loaded_faiss_index = FAISSIndex.load(
        str(FAISS_INDEX_PATH)
    )

    if loaded_faiss_index.index.ntotal != len(
        embedding_records
    ):

        raise RuntimeError(
            "Persisted FAISS index contains "
            "an unexpected number of vectors."
        )

    if len(
        loaded_faiss_index.metadata
    ) != len(
        embedding_records
    ):

        raise RuntimeError(
            "Persisted FAISS metadata count "
            "does not match embeddings."
        )

    print(
        "FAISS persistence validation passed."
    )

    print(
        f"Vectors: "
        f"{loaded_faiss_index.index.ntotal}"
    )

    print(
        f"Dimension: "
        f"{loaded_faiss_index.dimension}"
    )


    
    # ========================================================
    # PIPELINE COMPLETE
    # ========================================================

    print("\n" + "=" * 80) 
    print("PIPELINE COMPLETE") 
    print("=" * 80) 
    print( "ETL → parsing → normalization → validation " "→ chunking → embedding → FAISS indexing complete." )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
