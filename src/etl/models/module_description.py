from dataclasses import dataclass, asdict
from typing import Optional, Any

from src.etl.models.source import SourceRange


@dataclass
class ModuleDescription:

    # ========================================================
    # IDENTIFICATION
    # ========================================================

    module_code: str
    module_name: str
    category: str
    version: Optional[str] = None

    # ========================================================
    # RESPONSIBILITY
    # ========================================================

    responsible: Optional[str] = None

    # ========================================================
    # CONTENT AND LEARNING OBJECTIVES
    # ========================================================

    content: Optional[str] = None
    qualification_goals: Optional[str] = None

    # ========================================================
    # TEACHING
    # ========================================================

    teaching_forms: Optional[str] = None

    # ========================================================
    # PREREQUISITES
    # ========================================================

    prerequisites: Optional[str] = None

    # ========================================================
    # APPLICABILITY
    # ========================================================

    applicability: Optional[str] = None

    # ========================================================
    # CREDIT REQUIREMENTS
    # ========================================================

    credit_requirements: Optional[str] = None

    # ========================================================
    # EXAMINATION
    # ========================================================

    examination: Optional[str] = None

    # ========================================================
    # CREDITS AND GRADES
    # ========================================================

    credits_and_grades: Optional[str] = None

    # ========================================================
    # OFFERING
    # ========================================================

    frequency: Optional[str] = None

    # ========================================================
    # WORKLOAD
    # ========================================================

    workload: Optional[str] = None

    # ========================================================
    # DURATION
    # ========================================================

    duration: Optional[str] = None

    # ========================================================
    # SOURCE
    # ========================================================

    source: Optional[SourceRange] = None

    # ========================================================
    # CONVERSION
    # ========================================================

    def to_dict(self) -> dict[str, Any]:

        result = asdict(self)

        return result