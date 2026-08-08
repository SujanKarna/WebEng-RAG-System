from src.models.clean_block import CleanBlock, BlockRole
from src.models.segment import Segment
import re

def split(blocks: list[CleanBlock]) -> list[Segment]:
    segments = []
    order = 0

    for item in blocks:

        if item.role != BlockRole.CONTENT:
            continue

        text = item.block.text.strip()

        parts = split_heading_paragraph(text)

        offset = 0

        for part in parts:

            start = text.find(part, offset)
            end = start + len(part)

            segments.append(
                Segment(
                    block=item.block,
                    text=part,
                    order=order,
                    start=start,
                    end=end,
                )
            )

            order += 1
            offset = end

    return segments


def split_heading_paragraph(text: str) -> list[str]:
    """
    First splitting rule:
    Split after a § heading if a paragraph starts.
    """

    match = re.search(r"\(\d+\)", text)

    if not match:
        return [text]

    return [
        text[:match.start()].strip(),
        text[match.start():].strip(),
    ]