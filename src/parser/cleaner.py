import re

from src.models.block import Block
from src.models.clean_block import CleanBlock, BlockRole


TOP_MARGIN_THRESHOLD = 40
BOTTOM_MARGIN_THRESHOLD = 790

def clean(blocks: list[Block])-> list[CleanBlock]:
    cleaned = []
    for block in blocks:
        role = classify(block)

        cleaned.append(
            CleanBlock(
                block=block,
                role=role
            )
        )
    return cleaned


def classify(block: Block)-> BlockRole:
    text = block.text.strip()
    if re.fullmatch(r"\d{3,5}", text):
        return BlockRole.PAGE_NUMBER

    
    temp = text.replace("_", " ").replace("  ", " ").strip()
    if temp.startswith("Amtliche Bekanntmachungen"):
        return BlockRole.HEADER

    if temp.startswith("Nr. "):
        return BlockRole.HEADER

    if temp.startswith("vom "):
        return BlockRole.HEADER

    if block.y0 < TOP_MARGIN_THRESHOLD:
        return BlockRole.HEADER

    if block.y1 > BOTTOM_MARGIN_THRESHOLD:
        return BlockRole.FOOTER

    return BlockRole.CONTENT
