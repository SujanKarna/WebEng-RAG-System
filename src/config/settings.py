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
    / "chunks.jsonl"
)

EMBEDDINGS_PATH = (
    PROCESSED_DATA_DIR
    / "embeddings.json"
)


# ============================================================ 
# COMBINED REGULATION 
# ============================================================ 
COMBINED_REGULATION_PATH = ( 
    PROCESSED_DATA_DIR / "regulation" / "regulation_with_modules.json" 
    )


# =============================================================================
# LLM / GENERATION
# =============================================================================

LLM_BASE_URL = "http://localhost:1234/v1/chat/completions"
LLM_MODEL = "qwen/qwen3-4b-2507"

LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1000
LLM_TIMEOUT = 120

# ============================================================
# RAG / RETRIEVAL
# ============================================================

RETRIEVAL_TOP_K = 5
RETRIEVAL_CANDIDATE_K = 10

RETRIEVAL_MIN_SCORE = 0.60

# Metadata-aware retrieval
RETRIEVAL_REGULATION_BOOST = 0.05
RETRIEVAL_MODULE_BOOST = 0.05

# Keyword matching
RETRIEVAL_KEYWORD_BOOST = 0.08

FAISS_INDEX_PATH = (
    PROCESSED_DATA_DIR / "faiss_index"
)

# ============================================================
# RETRIEVAL RERANKING
# ============================================================

RETRIEVAL_TITLE_BOOST = 0.12

# ============================================================
# RAG GENERATION
# ============================================================

RAG_MAX_CONTEXT_CHUNKS = 5

RAG_SYSTEM_PROMPT = """
Du bist ein hilfreicher Assistent für die bereitgestellten Dokumente.

Beantworte die Frage des Nutzers ausschließlich anhand der
bereitgestellten Quellen.

Regeln:

Verwende nur Informationen, die in den bereitgestellten Quellen
enthalten sind.
Verwende kein eigenes Wissen und ergänze keine Informationen,
die nicht aus den Quellen hervorgehen.
Erfinde keine Fakten, Zahlen, Paragraphen, Module oder Regelungen.

Wenn die Quellen die Frage nicht ausreichend beantworten können,
antworte:

"Dazu enthalten die bereitgestellten Quellen keine ausreichenden Informationen."

Du darfst Informationen aus mehreren relevanten Quellen
miteinander kombinieren.
Beziehe dich bei sachlichen Aussagen auf die entsprechende Quelle
mit [Quelle N].
Verwende eine Quelle nur dann als Beleg, wenn ihr Inhalt die
Aussage tatsächlich unterstützt.
Antworte direkt, klar und möglichst kurz.
Antworte in der Sprache der Frage.
Erwähne keine internen technischen Details wie Retrieval,
Embeddings, FAISS, Chunks oder Scores.

Gib keine zusätzlichen Informationen außerhalb der Quellen aus.
""".strip()

RAG_USER_PROMPT_TEMPLATE = """
FRAGE:
{query}

QUELLEN:
{context}

Beantworte die Frage ausschließlich anhand dieser Quellen.
Wenn die Quellen keine ausreichende Antwort enthalten, sage dies
klar und erfinde keine Informationen.
""".strip()

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