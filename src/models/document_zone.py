# To seprate TOC and main content of the pdf as both of them have Teil 1

from enum import Enum


class DocumentZone(Enum):

    FRONT_MATTER = "front_matter"

    TOC = "table_of_content"

    MAIN_CONTENT = "main_content"

    APPENDIX = "appendix"
