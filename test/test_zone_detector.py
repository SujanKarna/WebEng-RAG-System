# from src.parser.zone_detector import detect_zones
# from src.models.document_zone import DocumentZone


# pdf = r"D:\colab tests\AB_2025_48_3.pdf"


# blocks = extract(pdf)

# mapping = build_page_mapping(blocks)


# attach_printed_pages(
#     blocks,
#     mapping
# )

# clean_blocks = clean(blocks)


# segments = split(clean_blocks)


# for i, segment in enumerate(segments):

#     print(
#         i,
#         "|",
#         segment.zone.value,
#         "|",
#         segment.text[:100]
#     )