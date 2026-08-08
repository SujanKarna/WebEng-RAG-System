from src.parser.extractor import extract
from src.parser.page_mapper import attach_printed_pages, build_page_mapping
from src.parser.cleaner import clean
from src.parser.segmenter import split
from src.parser.zone_detector import detect_zones
from src.models.clean_block import BlockRole
from src.parser.section_classification import SectionClassifier
from src.parser.content_section_detector import detect_content_sections
from src.models.section_type import SectionType
from src.models.document_zone import DocumentZone
from src.parser.structure_analyzer import StructureAnalyzer
from collections import Counter
from src.parser.toc_normalizer import split_toc_sections
from src.parser.main_content_normalizer import normalize_main_content
from src.utils.tree_printer import print_tree

pdf = r"D:\colab tests\AB_2025_48_3.pdf"


# -------------------------------------------------
# 1. Extract PDF blocks
# -------------------------------------------------

blocks = extract(pdf)



# -------------------------------------------------
# 2. Attach printed page numbers
# -------------------------------------------------

mapping = build_page_mapping(blocks)

attach_printed_pages(
    blocks,
    mapping
)



# -------------------------------------------------
# 3. Clean blocks
# -------------------------------------------------

clean_blocks = clean(blocks)



# -------------------------------------------------
# 4. Keep only real content
# -------------------------------------------------

content_blocks = [
    block
    for block in clean_blocks
    if block.role == BlockRole.CONTENT
]



# -------------------------------------------------
# 5. Create segments
# -------------------------------------------------

segments = split(content_blocks)



# -------------------------------------------------
# 6. Detect document zones
# -------------------------------------------------

segments = detect_zones(segments)



# -------------------------------------------------
# 2. Separate TOC and MAIN_CONTENT
# -------------------------------------------------
toc_segments = [
    s for s in segments
    if s.zone == DocumentZone.TOC
]
main_segments = [
    s for s in segments
    if s.zone == DocumentZone.MAIN_CONTENT
]


# for s in main_segments[:100]:

#     print(
#         "PAGE:",
#         s.block.printed_page,
#         "|",
#         "Content:",
#         s.content_section,
#         "|",
#         "section:",
#         s.section_type,
#         "|",
#         s.text[:200]
#     )


# -------------------------------------------------
# 2. Normalize TOC and MAIN_CONTENT
# -------------------------------------------------
toc_segments = split_toc_sections(toc_segments)


# -------------------------------------------------
# 5. classify MAIN_CONTENT
# -------------------------------------------------
# Analyze if the line in a block is 
classifier = SectionClassifier()
toc_segments = classifier.analyze(
    toc_segments
)
main_segments = classifier.analyze(
    main_segments
)
main_segments = normalize_main_content(main_segments, toc_segments)


# for s in main_segments[:50]:

#     print(
#         s.block.printed_page,
#         "|",
#         s.section_type,
#         "|",
#         s.text[:50]
#     )

# 3. Content section detection
main_segments = detect_content_sections(
    main_segments
)

# for s in main_segments:

#     print(
#         s.block.printed_page,
#         "|",
#         s.section_type,
#         "|",
#         s.content_section,
#         "|",
#         s.text[:50]
#     )

#-----------------------------------------
# 5. Build heirarchy
#-----------------------------------------

analyzer = StructureAnalyzer()


tree = analyzer.build_tree(
    main_segments
)


print_tree(tree)