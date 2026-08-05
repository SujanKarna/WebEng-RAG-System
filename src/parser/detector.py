from src.models.block import Block
from src.models.detected_block import DetectedBlock, BlockType
from src.parser.header_detector import find_repeated_headers


def detect(blocks : list[Block]) -> list[DetectedBlock]:

    repeated_headers = find_repeated_headers(blocks)

    detected = []

    for block in blocks:

        block_type, confidence, level = classify(
            block,
            repeated_headers
        )

        detected.append(
            DetectedBlock(
                block=block,
                type=block_type,
                confidence=confidence,
                level=level
            )
        )

    return detected



def classify(block: Block, repeated_headers):

    text = block.text.strip()


    # ----------------------------
    # Remove repeated headers
    # ----------------------------

    if text in repeated_headers:

        return (
            BlockType.TEXT,
            0.99,
            None
        )


    size = block.font_size


    # Document title
    if size >= 14:

        return (
            BlockType.HEADING,
            0.99,
            1
        )


    # ----------------------------
    # Parts
    # ----------------------------

    if text.startswith("Teil "):

        return (
            BlockType.HEADING,
            0.95,
            2
        )


    # ----------------------------
    # Sections
    # ----------------------------

    if text.startswith("§"):

        return (
            BlockType.HEADING,
            0.90,
            3
        )

    # Main headings
    if size >= 12 and block.is_bold:

        return (
            BlockType.HEADING,
            0.95,
            2
        )


    # Small headings
    if size >= 11 and block.is_bold:

        return (
            BlockType.HEADING,
            0.85,
            3
        )


    # Bold 10pt sections
    if size == 10 and block.is_bold:

        return (
            BlockType.HEADING,
            0.70,
            4
        )

   

    return (
        BlockType.TEXT,
        0.90,
        None
    )