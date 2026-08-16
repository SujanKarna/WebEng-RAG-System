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

