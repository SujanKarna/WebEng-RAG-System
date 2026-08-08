from src.models.document_node import DocumentNode
from src.models.document_zone import DocumentZone
from src.models.section_type import SectionType


# Defines hierarchy priority
LEVELS = {

    SectionType.PART: 1,

    SectionType.PARAGRAPH: 2,

    SectionType.SECTION: 2,

    SectionType.MODULE: 3,

    SectionType.MODULE_DESCRIPTION: 2,

    SectionType.TEXT: 4,
}


def build_tree(segments):

    """
    Build document hierarchy.

    Structure:

    PART
        |
        PARAGRAPH
            |
            TEXT


    STUDY PLAN

        SECTION
            |
            MODULE
                |
                TEXT


    MODULE DESCRIPTIONS

        MODULE_DESCRIPTION
              |
              TEXT
    """


    root = DocumentNode(
        segment=None,
        title="Studienordnung",
        node_type="DOCUMENT"
    )


    stack = [root]


    for segment in segments:


        # Ignore non-main content
        if segment.zone != DocumentZone.MAIN_CONTENT:
            continue


        section_type = segment.section_type


        # Ignore unknown segments
        if section_type is None:
            continue



        # ----------------------------------------
        # Create node
        # ----------------------------------------

        node = DocumentNode(
            segment=segment
        )


        current_level = LEVELS.get(
            section_type,
            99
        )


        # ----------------------------------------
        # Find correct parent
        # ----------------------------------------

        while len(stack) > 1:


            parent = stack[-1]

            parent_level = LEVELS.get(
                parent.node_type,
                0
            )


            if parent_level < current_level:
                break


            stack.pop()



        parent = stack[-1]


        node.parent = parent

        parent.children.append(node)


        stack.append(node)



    return root



def print_tree(node, level=0):

    indent = "    " * level


    # DOCUMENT node
    if node.node_type == "DOCUMENT":

        print(
            f"{indent}{node.node_type}: {node.title}"
        )

    else:

        print(
            f"{indent}{node.node_type}: {node.title}"
        )


        # print actual text
        if node.text:

            print(
                f"{indent}    CONTENT: {node.text[:120]}"
            )


    for child in node.children:

        print_tree(
            child,
            level + 1
        )