"""
Document Zone Detector
======================

Assigns a logical document zone to every extracted PDF block.

Document structure:

    INTRODUCTION
        ↓
    TOC
        ↓
    MAIN_REGULATIONS
        ↓
    STUDY_PLAN
        ↓
    MODULE_DESCRIPTIONS

Zone transitions are detected using textual markers.
No page numbers are hard-coded.
"""

from src.etl.models.document_zone import DocumentZone


# ============================================================
# STRUCTURAL MARKERS
# ============================================================

# Introduction → TOC
#
# IMPORTANT:
# We intentionally use ONLY "Inhaltsübersicht".
#
# "Inhaltsverzeichnis" appears earlier in the official
# publication header and must not trigger the transition.

TOC_START_MARKER = "Inhaltsübersicht"


# TOC → Main regulations

MAIN_REGULATIONS_START_MARKER = (
    "Teil 1 Allgemeine Bestimmungen"
)


# Main regulations → Study plan

STUDY_PLAN_START_MARKER = (
    "STUDIENABLAUFPLAN"
)


# Study plan → Module descriptions

MODULE_DESCRIPTIONS_START_MARKERS = [
    "Anlage 2",
    "Modulbeschreibungen",
]


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for marker matching.

    This does NOT modify the original PDF text.
    """

    return (
        text
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
        .lower()
    )


def get_block_text(block: dict) -> str:
    """
    Reconstruct the text contained in an extracted block.
    """

    text_parts = []

    for line in block.get(
        "lines",
        []
    ):

        line_text = "".join(
            span.get(
                "text",
                ""
            )
            for span in line.get(
                "spans",
                []
            )
        )

        if line_text.strip():

            text_parts.append(
                line_text.strip()
            )

    return " ".join(
        text_parts
    )


# ============================================================
# ZONE DETECTOR
# ============================================================

class ZoneDetector:
    """
    Stateful detector that processes blocks in document order.

    The current zone is inherited by subsequent blocks until
    another structural marker changes the zone.
    """

    def __init__(self):

        # The document always starts with publication/
        # introductory material.

        self.current_zone = (
            DocumentZone.INTRODUCTION
        )

    def detect_block_zone(
        self,
        block: dict,
    ) -> DocumentZone:
        """
        Determine the zone for one block.

        The block's text is inspected for structural markers.

        Returns
        -------
        DocumentZone
            Zone assigned to this block.
        """

        text = get_block_text(
            block
        )

        normalized = normalize_text(
            text
        )

        # ----------------------------------------------------
        # INTRODUCTION → TOC
        # ----------------------------------------------------

        if (
            self.current_zone
            == DocumentZone.INTRODUCTION
            and TOC_START_MARKER.lower()
            in normalized
        ):

            self.current_zone = (
                DocumentZone.TOC
            )

            return self.current_zone

        # ----------------------------------------------------
        # TOC → MAIN REGULATIONS
        # ----------------------------------------------------

        if (
            self.current_zone
            == DocumentZone.TOC
            and MAIN_REGULATIONS_START_MARKER.lower()
            in normalized
        ):

            self.current_zone = (
                DocumentZone.MAIN_REGULATIONS
            )

            return self.current_zone

        # ----------------------------------------------------
        # MAIN REGULATIONS → STUDY PLAN
        # ----------------------------------------------------

        if (
            self.current_zone
            == DocumentZone.MAIN_REGULATIONS
            and STUDY_PLAN_START_MARKER.lower()
            in normalized
        ):

            self.current_zone = (
                DocumentZone.STUDY_PLAN
            )

            return self.current_zone

        # ----------------------------------------------------
        # STUDY PLAN → MODULE DESCRIPTIONS
        # ----------------------------------------------------

        if (
            self.current_zone
            == DocumentZone.STUDY_PLAN
            and any(
                marker.lower() in normalized
                for marker in
                MODULE_DESCRIPTIONS_START_MARKERS
            )
        ):

            self.current_zone = (
                DocumentZone.MODULE_DESCRIPTIONS
            )

            return self.current_zone

        # ----------------------------------------------------
        # NO TRANSITION
        # ----------------------------------------------------

        return self.current_zone


# ============================================================
# ASSIGN ZONES TO DOCUMENT
# ============================================================

def assign_zones(
    pages: list[dict],
) -> list[dict]:
    """
    Assign a zone to every extracted block.

    The original extraction structure is preserved.

    Only one new field is added to each block:

        "zone": "<zone>"

    Parameters
    ----------
    pages:
        Raw extracted pages.

    Returns
    -------
    list[dict]
        Pages with zones assigned to blocks.
    """

    detector = ZoneDetector()

    zoned_pages = []

    for page in pages:

        # Copy page so that the original structure
        # isn't modified in-place.

        page_copy = page.copy()

        zoned_blocks = []

        for block in page.get(
            "blocks",
            []
        ):

            block_copy = block.copy()

            # Detect the zone.

            zone = detector.detect_block_zone(
                block
            )

            # Assign the enum's string value to JSON.
            #
            # Example:
            #
            # DocumentZone.INTRODUCTION
            #
            # becomes:
            #
            # "introduction"

            block_copy["zone"] = (
                zone.value
            )

            zoned_blocks.append(
                block_copy
            )

        page_copy["blocks"] = (
            zoned_blocks
        )

        zoned_pages.append(
            page_copy
        )

    return zoned_pages