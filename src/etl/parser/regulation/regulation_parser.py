import re
from typing import Any


class RegulationParser:
    """
    Reconstruct the main regulation from cleaned_blocks.json.

    The cleaned blocks are already ordered according to the PDF.

    The parser reconstructs the regulation into paragraph-level
    objects such as:

        § 1 Geltungsbereich
        § 2 Studienbeginn und Regelstudienzeit
        ...
        § 11 Inkrafttreten ...

    Headers, footers and page numbers are excluded.
    """

    # ========================================================
    # PATTERNS
    # ========================================================

    PART_PATTERN = re.compile(
        r"^Teil\s+(\d+)\s+(.+)$",
        re.IGNORECASE,
    )

    PARAGRAPH_PATTERN = re.compile(
        r"^§\s*(\d+)\s+(.+?)(?:\n|$)",
        re.DOTALL,
    )

    HEADER_PATTERN = re.compile(
        r"^Amtliche Bekanntmachungen\b",
        re.IGNORECASE,
    )

    ISSUE_PATTERN = re.compile(
        r"^Nr\.\s*\d+/\d+",
        re.IGNORECASE,
    )

    DATE_PATTERN = re.compile(
        r"^vom\s+\d{1,2}\.\s+\w+\s+\d{4}",
        re.IGNORECASE,
    )

    PAGE_NUMBER_PATTERN = re.compile(
        r"^\d{3,4}$"
    )


    
    PARAGRAPH_TITLES = {
    "1": "Geltungsbereich",
    "2": "Studienbeginn und Regelstudienzeit",
    "3": "Zugangsvoraussetzungen",
    "4": "Lehr- und Lernformen",
    "5": "Ziele des Studienganges",
    "6": "Aufbau des Studiums",
    "7": "Inhalte des Studiums",
    "8": "Studienberatung",
    "9": "Prüfungen",
    "10": "Fern- und Teilzeitstudium",
    "11": "Inkrafttreten und Veröffentlichung, Übergangsregelung",
}


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        blocks: list[dict[str, Any]],
    ) -> None:

        self.blocks = blocks

    # ========================================================
    # PUBLIC API
    # ========================================================

    def parse(self) -> list[dict[str, Any]]:
        """
        Reconstruct regulation paragraphs.
        """

        paragraphs: list[dict[str, Any]] = []

        current_part: dict[str, str] | None = None
        current_paragraph: dict[str, Any] | None = None

        for block in self.blocks:

            # ------------------------------------------------
            # Only process main regulation
            # ------------------------------------------------

            if block.get("zone") != "main_regulations":
                continue

            text = block.get("text", "").strip()

            if not text:
                continue

            # ------------------------------------------------
            # Remove headers / footers
            # ------------------------------------------------

            if self._is_page_furniture(text):
                continue

            # ------------------------------------------------
            # Detect Part
            # ------------------------------------------------

            part = self._parse_part(text)

            if part is not None:

                current_part = part

                continue

            # ------------------------------------------------
            # Detect paragraph
            # ------------------------------------------------

            paragraph = self._parse_paragraph(text)

            if paragraph is not None:

                # Finish previous paragraph
                if current_paragraph is not None:

                    paragraphs.append(
                        self._finalize_paragraph(
                            current_paragraph
                        )
                    )

                # Create new paragraph
                current_paragraph = {
                    "paragraph": paragraph["paragraph"],
                    "paragraph_title": paragraph["title"],
                    "part": current_part,
                    "blocks": [],
                }

                # Add body contained in the same block
                if paragraph["body"]:

                    self._append_block(
                        current_paragraph,
                        block,
                        paragraph["body"],
                    )

                continue

            # ------------------------------------------------
            # Normal continuation block
            # ------------------------------------------------

            if current_paragraph is not None:

                self._append_block(
                    current_paragraph,
                    block,
                    text,
                )

        # ----------------------------------------------------
        # Finish final paragraph
        # ----------------------------------------------------

        if current_paragraph is not None:

            paragraphs.append(
                self._finalize_paragraph(
                    current_paragraph
                )
            )

        return paragraphs

    # ========================================================
    # PAGE FURNITURE
    # ========================================================

    def _is_page_furniture(
        self,
        text: str,
    ) -> bool:

        if self.HEADER_PATTERN.match(text):
            return True

        if self.ISSUE_PATTERN.match(text):
            return True

        if self.DATE_PATTERN.match(text):
            return True

        if self.PAGE_NUMBER_PATTERN.fullmatch(text):
            return True

        return False

    # ========================================================
    # PART PARSER
    # ========================================================

    def _parse_part(
        self,
        text: str,
    ) -> dict[str, str] | None:

        match = self.PART_PATTERN.match(text)

        if match is None:
            return None

        return {
            "part": f"Teil {match.group(1)}",
            "part_title": match.group(2).strip(),
        }

    # ========================================================
    # PARAGRAPH PARSER
    # ========================================================

    def _parse_paragraph(
    self,
    text: str,
) -> dict[str, str] | None:

        match = re.match(
            r"^§\s*(\d+)\s+(.+)$",
            text,
            re.DOTALL,
        )

        if match is None:
            return None

        number = match.group(1)
        remainder = match.group(2).strip()

        expected_title = self.PARAGRAPH_TITLES.get(number)

        # --------------------------------------------------------
        # If we know the title, use it directly.
        # --------------------------------------------------------

        if expected_title is not None:

            if remainder.startswith(expected_title):

                body = remainder[
                    len(expected_title):
                ].strip()

                return {
                    "paragraph": f"§ {number}",
                    "title": expected_title,
                    "body": body,
                }

        # --------------------------------------------------------
        # Generic fallback
        # --------------------------------------------------------

        if "\n" in remainder:

            lines = [
                line.strip()
                for line in remainder.splitlines()
                if line.strip()
            ]

            title = lines[0]

            body = "\n".join(lines[1:])

            return {
                "paragraph": f"§ {number}",
                "title": title,
                "body": body,
            }

        return {
            "paragraph": f"§ {number}",
            "title": remainder,
            "body": "",
        }

    def _append_block(
        self,
        paragraph: dict[str, Any],
        block: dict[str, Any],
        text: str,
    ) -> None:

        if not text:
            return

        paragraph["blocks"].append(
            {
                "block_index": block.get("block_index"),
                "page_index": block.get("page_index"),
                "page_number": block.get("page_number"),
                "text": text,
            }
        )

    # ========================================================
    # FINALIZE PARAGRAPH
    # ========================================================

    def _finalize_paragraph(
        self,
        paragraph: dict[str, Any],
    ) -> dict[str, Any]:

        blocks = paragraph["blocks"]

        text_parts = [
            block["text"]
            for block in blocks
            if block["text"].strip()
        ]

        text = "\n".join(text_parts)

        pages = [
            block["page_number"]
            for block in blocks
            if block["page_number"] is not None
        ]

        result = {
            "paragraph": paragraph["paragraph"],
            "paragraph_title": paragraph["paragraph_title"],
            "part": paragraph["part"],
            "text": text,
            "page_start": min(pages) if pages else None,
            "page_end": max(pages) if pages else None,
            "blocks": blocks,
        }

        return result