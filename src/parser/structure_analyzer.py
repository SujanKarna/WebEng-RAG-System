from src.models.document_node import DocumentNode
from src.models.document_zone import DocumentZone
from src.models.section_type import SectionType
from src.models.content_section import ContentSection


class StructureAnalyzer:


    def build_tree(segments):

        root = DocumentNode(
            segment=None
        )

        root.node_type = "DOCUMENT"
        root.title = "Studienordnung"


        current_part = None
        current_paragraph = None
        current_section = None
        current_module = None
        current_module_description = None


        for segment in segments:


            # only main content
            if segment.zone != DocumentZone.MAIN_CONTENT:
                continue


            # -------------------------------------------------
            # PART
            # -------------------------------------------------

            if segment.section_type == SectionType.PART:

                current_part = DocumentNode(
                    segment=segment
                )

                root.children.append(current_part)

                current_paragraph = None
                current_section = None
                current_module = None

                continue



            # -------------------------------------------------
            # PARAGRAPH (§1, §2...)
            # -------------------------------------------------

            if segment.section_type == SectionType.PARAGRAPH:

                if current_part:

                    current_paragraph = DocumentNode(
                        segment=segment
                    )

                    current_part.children.append(
                        current_paragraph
                    )


                continue



            # -------------------------------------------------
            # STUDY PLAN TABLE SECTIONS
            # 1. Grundlagenmodule
            # -------------------------------------------------

            if segment.section_type == SectionType.SECTION:

                current_section = DocumentNode(
                    segment=segment
                )


                # study plan sections are after Teil 4
                if (
                    current_part
                    and current_part.segment.content_section
                    == ContentSection.FINAL_PROVISIONS
                ):

                    root.children.append(
                        current_section
                    )

                else:

                    if current_part:
                        current_part.children.append(
                            current_section
                        )


                current_module = None

                continue



            # -------------------------------------------------
            # MODULE TABLE ROW
            # -------------------------------------------------

            if segment.section_type == SectionType.MODULE:


                current_module = DocumentNode(
                    segment=segment
                )


                if current_section:

                    current_section.children.append(
                        current_module
                    )

                continue



            # -------------------------------------------------
            # MODULE DESCRIPTION
            # -------------------------------------------------

            if (
                segment.content_section
                == ContentSection.MODULE_DESCRIPTIONS
            ):


                if (
                    "modulnummer"
                    in segment.text.lower()
                ):

                    current_module_description = DocumentNode(
                        segment=segment
                    )


                    root.children.append(
                        current_module_description
                    )


                    current_module = (
                        current_module_description
                    )


                    continue



            # -------------------------------------------------
            # NORMAL TEXT
            # -------------------------------------------------

            text_node = DocumentNode(
                segment=segment
            )


            if current_module:

                current_module.children.append(
                    text_node
                )


            elif current_paragraph:

                current_paragraph.children.append(
                    text_node
                )


            elif current_part:

                current_part.children.append(
                    text_node
                )


        return root



    def print_tree(node, level=0):

        indent = "    " * level


        if node.segment:

            print(
                f"{indent}{node.segment.section_type}: "
                f"{node.segment.text[:80]}"
            )

        else:

            print(
                f"{indent}{node.node_type}: "
                f"{node.title}"
            )


        for child in node.children:

            print_tree(
                child,
                level + 1
            )