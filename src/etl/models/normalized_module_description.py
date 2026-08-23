"""
Normalized representation of a module description.

Contains the cleaned textual representation together with
structured values derived from the textual fields.
"""

from dataclasses import dataclass
from src.etl.models.source import SourceRange

@dataclass
class NormalizedModuleDescription:

    # ========================================================
    # Identity
    # ========================================================

    module_code: str | None
    module_name: str | None
    category: str | None
    version: str | None

    # ========================================================
    # Academic information
    # ========================================================

    responsible: str | None
    content: str | None
    qualification_goals: str | None
    teaching_forms: str | None
    prerequisites: str | None
    applicability: str | None
    credit_requirements: str | None
    examination: str | None
    credits_and_grades: str | None
    frequency: str | None
    workload: str | None
    duration: str | None

    # ========================================================
    # Structured values
    # ========================================================

    credits: int | None = None
    workload_as: int | None = None
    duration_semesters: int | None = None

    # ========================================================
    # Provenance
    # ========================================================

    source: SourceRange | None = None