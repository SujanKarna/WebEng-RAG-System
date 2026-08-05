from collections import Counter
from src.models.block import Block

def find_repeated_headers(
        blocks: list[Block], 
        threshold: int = 2
) -> set[str]:


    texts = []
    for block in blocks:
        text = block.text.strip()

        if text:
            texts.append(text)



    counts = Counter(texts)

    return {
        text
        for text, count in counts.items()
        if count >= threshold
    }