from src.parser.analyser import analyze_font_sizes
from src.parser.extractor import extract
from src.parser.detector import detect



pdf = r"D:\colab tests\AB_2025_48_3.pdf"


blocks = extract(pdf)
    


detected = detect(blocks)


for item in detected[:20]:

    print(
        item.type.value,
        "level=",
        item.level,
        "=>",
        item.block.text[:80]
    )