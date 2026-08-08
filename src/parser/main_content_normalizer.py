import copy
import re

from src.models.section_type import SectionType


def normalize_main_content(main_content, toc_segments):
    """
    Split MAIN_CONTENT paragraph headings from their body.

    The TOC is used as the authoritative source for
    paragraph headings.

    Example:

        MAIN:
        § 1Geltungsbereich Diese Studienordnung regelt ...

        TOC:
        § 1Geltungsbereich

        RESULT:
        PARAGRAPH -> § 1Geltungsbereich
        TEXT      -> Diese Studienordnung regelt ...
    """

    toc_headings = build_toc_heading_map(
        toc_segments
    )

    result = []

    for segment in main_content:

        text = segment.text.strip()

        paragraph_number = extract_paragraph_number(
            text
        )

        # ------------------------------------------------
        # Not a paragraph candidate
        # ------------------------------------------------

        if paragraph_number is None:

            result.append(segment)

            continue


        # ------------------------------------------------
        # Find corresponding TOC heading
        # ------------------------------------------------

        toc_heading = toc_headings.get(
            paragraph_number
        )

        if toc_heading is None:

            result.append(segment)

            continue


        # ------------------------------------------------
        # Check whether MAIN starts with TOC heading
        # ignoring whitespace differences
        # ------------------------------------------------

        split_position = find_heading_end(
            text,
            toc_heading
        )

        if split_position is None:

            result.append(segment)

            continue


        # ------------------------------------------------
        # Create paragraph segment
        # ------------------------------------------------

        paragraph = copy.copy(segment)

        paragraph.text = toc_heading

        paragraph.section_type = (
            SectionType.PARAGRAPH
        )

        result.append(paragraph)


        # ------------------------------------------------
        # Remaining body
        # ------------------------------------------------

        remainder = text[
            split_position:
        ].strip()


        if remainder:

            body = copy.copy(segment)

            body.text = remainder

            # IMPORTANT:
            # We are normalizing BEFORE StructureAnalyzer.
            # Therefore this is initially TEXT.

            body.section_type = SectionType.TEXT

            result.append(body)


    return result


# ========================================================
# TOC
# ========================================================


def build_toc_heading_map(toc_segments):

    headings = {}

    for segment in toc_segments:

        if segment.section_type != SectionType.PARAGRAPH:
            continue

        text = segment.text.strip()

        number = extract_paragraph_number(
            text
        )

        if number is not None:

            headings[number] = text


    return headings


# ========================================================
# PARAGRAPH NUMBER
# ========================================================


def extract_paragraph_number(text):

    match = re.match(
        r"^§\s*(\d+)",
        text.strip()
    )

    if not match:
        return None

    return int(match.group(1))


# ========================================================
# FIND END OF HEADING
# ========================================================


def find_heading_end(
    main_text,
    toc_heading
):
    """
    Find where the TOC heading ends inside MAIN_CONTENT.

    Whitespace is ignored during comparison.

    Example:

        MAIN:
        § 2Studienbeginn und Regelstudienzeit

        TOC:
        § 2 Studienbeginn und Regelstudienzeit

    They are considered equal.
    """

    main_index = 0
    toc_index = 0

    while (
        main_index < len(main_text)
        and toc_index < len(toc_heading)
    ):

        # Skip whitespace in MAIN
        if main_text[main_index].isspace():

            main_index += 1
            continue


        # Skip whitespace in TOC
        if toc_heading[toc_index].isspace():

            toc_index += 1
            continue


        # Compare characters
        if (
            main_text[main_index].lower()
            != toc_heading[toc_index].lower()
        ):

            return None


        main_index += 1
        toc_index += 1


    # Make sure the entire TOC heading was consumed

    while toc_index < len(toc_heading):

        if not toc_heading[toc_index].isspace():

            return None

        toc_index += 1


    return main_index