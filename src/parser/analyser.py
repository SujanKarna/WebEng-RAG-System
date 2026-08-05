from collections import Counter
from src.models.block import Block


def analyze_font_sizes(blocks: list[Block]):
    sizes = [
        round(block.font_size, 1) 
        for block in blocks 
        ]

    counter = Counter(sizes)
    print("Font size distribution:")

    for size, count in counter.most_common():
        print(
            f"{size}: {count} blocks"
        )