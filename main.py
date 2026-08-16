# ============================================================
# IMPORTS
# ============================================================

from src.config.settings import (
    TU_CHEMNITZ_WEB_ENGINEERING_2025_URL,
    WEB_ENGINEERING_2025_PATH,
    PROVENANCE_PATH,
    RAW_EXTRACTION_PATH,
    CLEANED_EXTRACTION_PATH
)

from src.etl.extract.downloader import download_file

from src.etl.models.provenance import (
    create_provenance,
    save_provenance,
)
from src.etl.extract.pdf_extractor import extract_pdf, save_extraction
from src.etl.parser.cleaner import (
    clean_extraction_file,
)


# ============================================================
# DOCUMENT CONFIGURATION
# ============================================================

# Unique identifier for this exact logical document.
#
# This ID is used throughout the pipeline to connect:
# - the original PDF
# - extracted content
# - chunks
# - embeddings
# - vector database records
# - RAG citations
#
DOCUMENT_ID = "tuc_web_engineering_2025_study_regulation"


# ============================================================
# MAIN ETL PIPELINE
# ============================================================

def main():
    """
    Execute the document ingestion pipeline.

    Current pipeline stages:

        1. Download source document
        2. Generate provenance metadata

    Future stages will include:

        3. PDF extraction
        4. Page-number mapping
        5. Document cleaning
        6. Zone detection
        7. Section detection
        8. Structure analysis
        9. Semantic chunking
        10. Embedding generation
        11. Vector database ingestion
    """

    # --------------------------------------------------------
    # STAGE 1: DOCUMENT ACQUISITION
    # --------------------------------------------------------
    #
    # Download the official TU Chemnitz Web Engineering
    # 2025 Study Regulation from its source URL.
    #
    # The downloader is responsible for:
    #
    # - HTTP request
    # - PDF validation
    # - saving the PDF locally
    # - calculating the SHA-256 hash
    #
    # It does NOT perform PDF parsing.
    #

    print("=" * 60)
    print("STAGE 1: DOCUMENT ACQUISITION")
    print("=" * 60)

    print("Downloading TU Chemnitz study regulation...")

    download_metadata = download_file(
        url=TU_CHEMNITZ_WEB_ENGINEERING_2025_URL,
        destination=WEB_ENGINEERING_2025_PATH,
    )

    print("Download completed.")
    print(f"File: {WEB_ENGINEERING_2025_PATH}")
    print(f"SHA-256: {download_metadata['sha256']}")
    print()


    # --------------------------------------------------------
    # STAGE 2: PROVENANCE CREATION
    # --------------------------------------------------------
    #
    # Store information about the source document.
    #
    # Provenance allows us to answer questions such as:
    #
    # - Where did this document come from?
    # - Which version was processed?
    # - When was it downloaded?
    # - What was its SHA-256 hash?
    # - Which exact source document produced our chunks?
    #
    # This becomes especially important when the RAG system
    # provides citations to the user.
    #

    print("=" * 60)
    print("STAGE 2: PROVENANCE CREATION")
    print("=" * 60)

    provenance = create_provenance(
        document_id=DOCUMENT_ID,
        title=(
            "Studienordnung für den englischsprachigen "
            "konsekutiven Studiengang Web Engineering"
        ),
        university="Technische Universität Chemnitz",
        degree_program="Web Engineering",
        document_type="Studienordnung",
        regulation_version="2025",
        source_url=download_metadata["url"],
        local_filename=download_metadata["filename"],
        sha256=download_metadata["sha256"],
        size_bytes=download_metadata["size_bytes"],
    )

    save_provenance(
        provenance=provenance,
        path=PROVENANCE_PATH,
    )

    print("Provenance created.")
    print(f"Metadata: {PROVENANCE_PATH}")
    print()
    

    # --------------------------------------------------------
    # STAGE 3: PDF EXTRACTION
    # --------------------------------------------------------
    #
    # Extract the raw structural representation of the PDF.
    #
    # Nothing is cleaned or interpreted at this stage.
    #
    # We preserve:
    #
    # - page information
    # - page dimensions
    # - blocks
    # - lines
    # - spans
    # - bounding boxes
    # - fonts
    # - font sizes
    # - font flags
    #
    # The raw extraction is persisted so that later pipeline
    # stages can be reproduced without re-processing the PDF.
    #

    print("=" * 60)
    print("STAGE 3: PDF EXTRACTION")
    print("=" * 60)

    print("Extracting PDF structure...")

    pages = extract_pdf(
        pdf_path=WEB_ENGINEERING_2025_PATH
    )

    print(
        f"Extracted {len(pages)} pages."
    )

    total_blocks = sum(
        len(page["blocks"])
        for page in pages
    )

    print(
        f"Extracted {total_blocks} blocks."
    )

    # --------------------------------------------------------
    # SAVE RAW EXTRACTION
    # --------------------------------------------------------

    print(
        "Saving raw extraction..."
    )

    save_extraction(
        pages=pages,
        output_path=RAW_EXTRACTION_PATH,
    )

    print(
        f"Raw extraction saved to: "
        f"{RAW_EXTRACTION_PATH}"
    )

    print()


    # --------------------------------------------------------
    # EXTRACTION INSPECTION
    # --------------------------------------------------------
    #
    # Display a small sample of the extracted structure.
    # This is temporary debugging output and can later be
    # replaced by logging.
    #

    first_page = pages[0]

    print("\nFirst page:")
    print(
        f"Page index: {first_page['page_index']}"
    )
    print(
        f"Page number: {first_page['page_number']}"
    )
    print(
        f"Dimensions: "
        f"{first_page['width']} x "
        f"{first_page['height']}"
    )

    print(
        f"Blocks: {len(first_page['blocks'])}"
    )

    for block in first_page["blocks"][:3]:

        print(
            f"\nBlock {block['block_index']}"
        )

        for line in block["lines"]:

            text = "".join(
                span["text"]
                for span in line["spans"]
            )

            print(
                f"  {text}"
            )



    # ========================================================
    # STAGE 4: TEXT CLEANING
    # ========================================================
    #
    # Clean the raw PDF extraction.
    #
    # Responsibilities:
    #
    # - reconstruct block text
    # - normalize whitespace
    # - repair PDF line-wrap hyphenation
    # - remove empty blocks
    # - identify standalone page numbers
    # - preserve page/block provenance
    #
    # IMPORTANT:
    #
    # Study-plan tables are NOT processed here.
    #
    # The cleaner operates only on the raw text extraction.
    #
    # Study-plan handling will be performed outside this
    # text-cleaning stage.
    #

    print("=" * 60)
    print("STAGE 4: TEXT CLEANING")
    print("=" * 60)

    print("Cleaning extracted text...")

    clean_extraction_file(
        input_path=RAW_EXTRACTION_PATH,
        output_path=CLEANED_EXTRACTION_PATH,
    )

    print(
        f"Cleaned extraction saved to: "
        f"{CLEANED_EXTRACTION_PATH}"
    )

    print()
# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()