"""
Text Reconstructor Test
=======================

Tests text reconstruction independently from the rest of
the document pipeline.
"""

from pathlib import Path
import sys


# ============================================================================
# PROJECT ROOT
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# IMPORT
# ============================================================================

from src.etl.parser.text_reconstructor import (
    reconstruct_text,
    reconstruct_blocks,
)


# ============================================================================
# TEST CASES
# ============================================================================

def test_hyphenation():

    text = """Software Service Enginee-
ring"""

    result = reconstruct_text(text)

    print("\n" + "=" * 80)
    print("TEST: HYPHENATION")
    print("=" * 80)

    print("INPUT:")
    print(text)

    print("\nOUTPUT:")
    print(result)

    assert result == "Software Service Engineering"


def test_normal_line_breaks():

    text = """Der Studiengang hat eine Regelstudienzeit von vier
Semestern (zwei Jahren), bei einem Studium in
Teilzeit von acht Semestern (vier Jahren)."""

    result = reconstruct_text(text)

    print("\n" + "=" * 80)
    print("TEST: NORMAL LINE BREAKS")
    print("=" * 80)

    print("INPUT:")
    print(text)

    print("\nOUTPUT:")
    print(result)

    expected = (
        "Der Studiengang hat eine Regelstudienzeit von vier "
        "Semestern (zwei Jahren), bei einem Studium in "
        "Teilzeit von acht Semestern (vier Jahren)."
    )

    assert result == expected


def test_paragraph_markers():

    text = """(1) Ein Studienbeginn ist in der Regel im
Wintersemester möglich.
(2) Der Studiengang hat eine Regelstudienzeit
von vier Semestern."""

    result = reconstruct_text(text)

    print("\n" + "=" * 80)
    print("TEST: PARAGRAPH MARKERS")
    print("=" * 80)

    print("INPUT:")
    print(text)

    print("\nOUTPUT:")
    print(result)

    expected = (
        "(1) Ein Studienbeginn ist in der Regel im "
        "Wintersemester möglich.\n"
        "(2) Der Studiengang hat eine Regelstudienzeit "
        "von vier Semestern."
    )

    assert result == expected


def test_section_marker():

    text = """§ 3
Zugangsvoraussetzungen
(1) Die Zugangsvoraussetzungen für den
Masterstudiengang Web Engineering."""

    result = reconstruct_text(text)

    print("\n" + "=" * 80)
    print("TEST: SECTION MARKER")
    print("=" * 80)

    print("INPUT:")
    print(text)

    print("\nOUTPUT:")
    print(result)


def test_bullets():

    text = """Lehrformen:
• Vorlesung
• Seminar
• Übung
• Projekt"""

    result = reconstruct_text(text)

    print("\n" + "=" * 80)
    print("TEST: BULLETS")
    print("=" * 80)

    print("INPUT:")
    print(text)

    print("\nOUTPUT:")
    print(result)

    expected = (
        "Lehrformen:\n"
        "• Vorlesung\n"
        "• Seminar\n"
        "• Übung\n"
        "• Projekt"
    )

    assert result == expected


def test_block_provenance():

    blocks = [
        {
            "block_index": 42,
            "page_index": 5,
            "page_number": 6,
            "zone": "main_regulations",
            "text": """Der Studiengang hat eine Regelstudienzeit von vier
Semestern."""
        }
    ]

    result = reconstruct_blocks(blocks)

    print("\n" + "=" * 80)
    print("TEST: BLOCK PROVENANCE")
    print("=" * 80)

    print(result[0])

    assert result[0]["block_index"] == 42
    assert result[0]["page_index"] == 5
    assert result[0]["page_number"] == 6
    assert result[0]["zone"] == "main_regulations"

    assert result[0]["text"] == (
        "Der Studiengang hat eine Regelstudienzeit von vier Semestern."
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("TEXT RECONSTRUCTOR TEST")
    print("=" * 80)

    test_hyphenation()
    test_normal_line_breaks()
    test_paragraph_markers()
    test_section_marker()
    test_bullets()
    test_block_provenance()

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)