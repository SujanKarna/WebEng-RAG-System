"""
Module Description Normalizer

Normalizes parsed ModuleDescription objects without changing
their semantic content.

Responsibilities:
- normalize whitespace
- normalize empty values
- normalize placeholders such as "---"
- normalize module codes
- normalize version values
- extract structured numeric values such as credits and workload
- preserve the original ModuleDescription
"""

import re
from copy import deepcopy

from src.etl.models.module_description import ModuleDescription
from src.etl.models.normalized_module_description import (
    NormalizedModuleDescription,
)

# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: str | None) -> str | None:
    """
    Normalize whitespace while preserving the actual text.
    """

    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    # Normalize repeated whitespace.
    value = re.sub(r"\s+", " ", value)

    # Normalize common PDF artifacts.
    value = value.replace(" - ", "-")

    return value


# ============================================================
# EMPTY / PLACEHOLDER VALUES
# ============================================================

EMPTY_VALUES = {
    "",
    "---",
    "–",
    "—",
    "nicht angegeben",
    "keine Angabe",
}


def normalize_optional_text(
    value: str | None,
) -> str | None:

    if value is None:
        return None

    value = normalize_text(value)

    if value is None:
        return None

    if value.lower() in {
        item.lower()
        for item in EMPTY_VALUES
    }:
        return None

    return value


# ============================================================
# MODULE CODE
# ============================================================

MODULE_CODE_PATTERN = re.compile(
    r"^\s*(\d{6}-\d{3})\s*$"
)


def normalize_module_code(
    value: str | None,
) -> str | None:

    value = normalize_optional_text(value)

    if value is None:
        return None

    match = MODULE_CODE_PATTERN.match(value)

    if match:
        return match.group(1)

    return value


# ============================================================
# VERSION
# ============================================================

VERSION_PATTERN = re.compile(
    r"(\d+)"
)


def normalize_version(
    value: str | None,
) -> str | None:

    value = normalize_optional_text(value)

    if value is None:
        return None

    match = VERSION_PATTERN.search(value)

    if match:
        return match.group(1)

    return value


# ============================================================
# CREDITS
# ============================================================

CREDITS_PATTERN = re.compile(
    r"(\d+)\s*Leistungspunkte"
)


def extract_credits(
    value: str | None,
) -> int | None:

    if not value:
        return None

    match = CREDITS_PATTERN.search(value)

    if not match:
        return None

    return int(match.group(1))


# ============================================================
# WORKLOAD
# ============================================================

WORKLOAD_PATTERN = re.compile(
    r"(\d+)\s*AS"
)


def extract_workload(
    value: str | None,
) -> int | None:

    if not value:
        return None

    match = WORKLOAD_PATTERN.search(value)

    if not match:
        return None

    return int(match.group(1))


# ============================================================
# DURATION
# ============================================================

DURATION_PATTERN = re.compile(
    r"(\d+)\s*Semester",
    re.IGNORECASE,
)


def extract_duration_semesters(
    value: str | None,
) -> int | None:

    if not value:
        return None

    match = DURATION_PATTERN.search(value)

    if not match:
        return None

    return int(match.group(1))


# ============================================================
# NORMALIZE MODULE
# ============================================================

def normalize_module(
    module: ModuleDescription,
) -> NormalizedModuleDescription:

    return NormalizedModuleDescription(

        # ----------------------------------------------------
        # Identity
        # ----------------------------------------------------

        module_code=normalize_module_code(
            module.module_code
        ),

        module_name=normalize_optional_text(
            module.module_name
        ),

        category=normalize_optional_text(
            module.category
        ),

        version=normalize_version(
            module.version
        ),

        # ----------------------------------------------------
        # Academic information
        # ----------------------------------------------------

        responsible=normalize_optional_text(
            module.responsible
        ),

        content=normalize_optional_text(
            module.content
        ),

        qualification_goals=normalize_optional_text(
            module.qualification_goals
        ),

        teaching_forms=normalize_optional_text(
            module.teaching_forms
        ),

        prerequisites=normalize_optional_text(
            module.prerequisites
        ),

        applicability=normalize_optional_text(
            module.applicability
        ),

        credit_requirements=normalize_optional_text(
            module.credit_requirements
        ),

        examination=normalize_optional_text(
            module.examination
        ),

        credits_and_grades=normalize_optional_text(
            module.credits_and_grades
        ),

        frequency=normalize_optional_text(
            module.frequency
        ),

        workload=normalize_optional_text(
            module.workload
        ),

        duration=normalize_optional_text(
            module.duration
        ),

        # ----------------------------------------------------
        # Structured values
        # ----------------------------------------------------

        credits=extract_credits(
            module.credits_and_grades
        ),

        workload_as=extract_workload(
            module.workload
        ),

        duration_semesters=extract_duration_semesters(
            module.duration
        ),

        # ----------------------------------------------------
        # Provenance
        # ----------------------------------------------------

        source = module.source,
    )


def normalize_modules(
    modules: list[ModuleDescription],
) -> list[NormalizedModuleDescription]:

    return [
        normalize_module(module)
        for module in modules
    ]