from src.models.document_zone import DocumentZone


def detect_zones(segments):

    zone = DocumentZone.FRONT_MATTER


    for segment in segments:

        text = segment.text.strip()


        if is_toc_start(text):

            zone = DocumentZone.TOC


        elif is_main_content_start(text):

            zone = DocumentZone.MAIN_CONTENT


        elif is_appendix_start(text):

            zone = DocumentZone.APPENDIX


        segment.zone = zone


    return segments



def is_toc_start(text)-> bool:

    return (
        "Inhaltsverzeichnis" in text
        or
        "Inhaltsübersicht" in text
    )



def is_main_content_start(text)->bool:

    return (
        text.startswith("Teil 1")
        and ":" not in text[:10]
    )



def is_appendix_start(text)->bool:

    return text.startswith("Anlagen")