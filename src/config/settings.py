from pathlib import Path


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------
# Data directories
# ---------------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
METADATA_DIR = DATA_DIR / "metadata"

PROCESSED_DATA_DIR = DATA_DIR / "processed"
# ---------------------------------------------------------
# TU Chemnitz source
# ---------------------------------------------------------

TU_CHEMNITZ_WEB_ENGINEERING_2025_URL = (
    "https://www.tu-chemnitz.de/verwaltung/studentenamt/abt11/ordnungen/2025/AB_2025_48_3.pdf"
)


# ---------------------------------------------------------
# Local file
# ---------------------------------------------------------

WEB_ENGINEERING_2025_FILENAME = (
    "tu_chemnitz_web_engineering_2025.pdf"
)

WEB_ENGINEERING_2025_PATH = (
    RAW_DATA_DIR / WEB_ENGINEERING_2025_FILENAME
)


# ---------------------------------------------------------
# Provenance
# ---------------------------------------------------------

PROVENANCE_PATH = (
    METADATA_DIR / "provenance.json"
)

# ---------------------------------------------------------
# Extraction output
# ---------------------------------------------------------

EXTRACTED_DATA_DIR = DATA_DIR / "extracted"

RAW_EXTRACTION_PATH = (
    EXTRACTED_DATA_DIR /
    "tu_chemnitz_web_engineering_2025_raw.json"
)

# ---------------------------------------------------------
# Cleaned extraction
# ---------------------------------------------------------

CLEANED_DATA_DIR = DATA_DIR / "cleaned"

CLEANED_EXTRACTION_PATH = (
    CLEANED_DATA_DIR
    / "tu_chemnitz_web_engineering_2025_cleaned.json"
)

# =============================================================================
# PROCESSED FILES
# =============================================================================

CLEANED_BLOCKS_PATH = (
    PROCESSED_DATA_DIR
    / "cleaned_blocks.json"
)

TOC_PATH = (
    PROCESSED_DATA_DIR
    / "toc.json"
)


CHUNKS_DIR = (
    PROCESSED_DATA_DIR /
    "chunks"
)


# ---------------------------------------------------------
# Main regulation
# ---------------------------------------------------------

PARSED_MAIN_REGULATION_PATH = (
    PROCESSED_DATA_DIR
    / "parsed_main_regulation.json"
)


# ---------------------------------------------------------
# Module descriptions
# ---------------------------------------------------------

PARSED_MODULE_DESCRIPTIONS_PATH = (
    PROCESSED_DATA_DIR
    / "parsed_module_descriptions.json"
)

NORMALIZED_MODULE_DESCRIPTIONS_PATH = (
    PROCESSED_DATA_DIR
    / "normalized_module_descriptions.json"
)


# ---------------------------------------------------------
# Final regulation structure
# ---------------------------------------------------------

REGULATION_STRUCTURE_PATH = (
    PROCESSED_DATA_DIR
    / "regulation_structure.json"
)


NORMALIZED_MAIN_REGULATION_PATH = (
    PROCESSED_DATA_DIR
    / "normalized_main_regulation.json"
)


# ============================================================
# RAG CHUNKING
# ============================================================

CHUNKS_PATH = (
    PROCESSED_DATA_DIR
    / "web_engineering_2025_chunks.jsonl"
)




# ============================================================ 
# COMBINED REGULATION 
# ============================================================ 
COMBINED_REGULATION_PATH = ( 
    PROCESSED_DATA_DIR / "regulation" / "regulation_with_modules.json" 
    )


# ---------------------------------------------------------
# Directory helper
# ---------------------------------------------------------

def ensure_data_directories():
    """
    Create all required data directories if they do not exist.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACTED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)