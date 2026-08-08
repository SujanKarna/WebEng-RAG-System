import re

from src.models.section_type import SectionType
from src.models.segment import Segment


class SectionClassifier:
    """
    Detects the structural role of a segment.

    Input:
        list[Segment]

    Output:
        list[Segment] with section_type assigned
    """

    def analyze(self, segments: list[Segment]) -> list[Segment]:

        for segment in segments:

            segment.section_type = self.detect_type(segment.text)

        return segments


    def detect_type(self, text: str) -> SectionType:

        text = text.strip()

        if not text:
            return SectionType.TEXT


        if self.is_paragraph(text):
            return SectionType.PARAGRAPH


        if self.is_part(text):
            return SectionType.PART


        if self.is_subsection(text):
            return SectionType.SUBSECTION


        if self.is_section(text):
            return SectionType.SECTION

        if self.is_module(text):
            return SectionType.MODULE

        return SectionType.TEXT



    def is_paragraph(self, text: str) -> bool:
        """
        Examples:

        § 1
        § 1 Allgemeines
        §1 Geltungsbereich
        """

        return bool(
            re.match(
                r"^§\s*\d+",
                text
            )
        )

    def is_module(self, text: str) -> bool:
        return bool(
            re.match(
                r"^\d{6}-\d{3}",
                text
            )
        )

    def is_part(self, text: str) -> bool:
        """
        Examples:

        Teil 1
        Teil A
        """

        return bool(
            re.match(
                r"^Teil\s+[A-Za-z0-9]+",
                text,
                re.IGNORECASE
            )
        )


    def is_subsection(self, text: str) -> bool:
        """
        Examples:

        1.1 Grundlagen
        2.3 Wahlpflichtmodule
        """

        return bool(
            re.match(
                r"^\d+\.\d+",
                text
            )
        )


    def is_section(self, text: str) -> bool:
        """
        Examples:

        1. Grundlagenmodule
        2. Vertiefungsmodule
        """

        return bool(
            re.match(
                r"^\d+\.\s+",
                text
            )
        )