from src.models.content_section import ContentSection
from src.models.document_zone import DocumentZone
from src.models.section_type import SectionType


def detect_content_sections(segments):

    current_section = ContentSection.UNKNOWN

    document_phase = "REGULATION"


    for segment in segments:

        if segment.zone != DocumentZone.MAIN_CONTENT:
            continue


        text = segment.text.lower().strip()



        # ==================================================
        # Detect STUDIENABLAUFPLAN table
        # ==================================================

        if (
            document_phase != "MODULE_TABLE"
            and text == "studienablaufplan"
        ):

            document_phase = "STUDY_PLAN"

            current_section = (
                ContentSection.STUDY_PLAN
            )

            segment.content_section = current_section
            continue



        # ==================================================
        # Detect module description table
        # ==================================================

        if (
            text == "grundlagenmodul"
            and document_phase == "STUDY_PLAN"
        ):

            document_phase = "MODULE_TABLE"

            current_section = (
                ContentSection.MODULE_DESCRIPTIONS
            )

            segment.content_section = current_section
            continue



        # ==================================================
        # Normal regulation parts
        # ==================================================

        if document_phase == "REGULATION":

            if segment.section_type == SectionType.PART:

                if "teil 1" in text:
                    current_section = (
                        ContentSection.GENERAL_PROVISIONS
                    )

                elif "teil 2" in text:
                    current_section = (
                        ContentSection.STUDY_STRUCTURE
                    )

                elif "teil 3" in text:
                    current_section = (
                        ContentSection.STUDY_IMPLEMENTATION
                    )

                elif "teil 4" in text:
                    current_section = (
                        ContentSection.FINAL_PROVISIONS
                    )



        # ==================================================
        # Assign
        # ==================================================

        segment.content_section = current_section


    return segments