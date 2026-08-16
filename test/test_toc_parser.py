"""
Test TOC Parser
"""

from src.etl.parser.toc.toc_parser import (
    parse_toc,
)


def test_toc_parser():

    blocks = [

        {
            "block_index": 1,
            "page_index": 0,
            "page_number": 1,
            "zone": "table_of_contents",
            "text": "Inhaltsübersicht",
        },

        {
            "block_index": 2,
            "page_index": 1,
            "page_number": 2,
            "zone": "table_of_contents",
            "text": "Teil 1 Allgemeine Bestimmungen",
        },

        {
            "block_index": 3,
            "page_index": 1,
            "page_number": 2,
            "zone": "table_of_contents",
            "text": "§ 1 Geltungsbereich",
        },

        {
            "block_index": 4,
            "page_index": 1,
            "page_number": 2,
            "zone": "table_of_contents",
            "text": "§ 2 Studienbeginn und Regelstudienzeit",
        },

        {
            "block_index": 5,
            "page_index": 1,
            "page_number": 2,
            "zone": "table_of_contents",
            "text": "Teil 2 Aufbau und Inhalte des Studiums",
        },

        {
            "block_index": 6,
            "page_index": 1,
            "page_number": 2,
            "zone": "table_of_contents",
            "text": "§ 6 Aufbau des Studiums",
        },

        {
            "block_index": 7,
            "page_index": 1,
            "page_number": 2,
            "zone": "table_of_contents",
            "text": "§ 7 Inhalte des Studiums",
        },
    ]

    result = parse_toc(blocks)

    assert len(result["parts"]) == 2

    # ------------------------------------------------------------------
    # Part 1
    # ------------------------------------------------------------------

    part1 = result["parts"][0]

    assert part1["part"] == "Teil 1"
    assert part1["title"] == "Allgemeine Bestimmungen"

    assert len(part1["regulations"]) == 2

    assert part1["regulations"][0] == {
        "paragraph": "§ 1",
        "title": "Geltungsbereich",
    }

    assert part1["regulations"][1] == {
        "paragraph": "§ 2",
        "title": "Studienbeginn und Regelstudienzeit",
    }

    # ------------------------------------------------------------------
    # Part 2
    # ------------------------------------------------------------------

    part2 = result["parts"][1]

    assert part2["part"] == "Teil 2"
    assert part2["title"] == "Aufbau und Inhalte des Studiums"

    assert len(part2["regulations"]) == 2

    print("\nTOC PARSER TEST PASSED")


if __name__ == "__main__":
    test_toc_parser()