from enum import Enum

class DocumentZone(Enum):
    INTRODUCTION = 'introduction'
    TOC = 'table_of_contents'
    MAIN_REGULATIONS = 'main_regulations'
    STUDY_PLAN = 'study_plan'
    MODULE_DESCRIPTIONS ='module_descriptions'
    UNKNOWN ='unknown'