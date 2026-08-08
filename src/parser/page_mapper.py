import re
from src.models.block import Block


def build_page_mapping(blocks: list[Block]) -> dict[int, int]:

    mapping: dict[int, int] = {}

    for block in blocks:
        text = block.text.strip()

        if re.fullmatch(r"\d{3,5}", text):
            mapping[block.pdf_page] = int(text)

    return mapping


def attach_printed_pages(blocks: list[Block], mapping: dict[int, int]) -> None:

    for block in blocks:
        if block.pdf_page in mapping:
            block.printed_page = mapping[block.pdf_page]
