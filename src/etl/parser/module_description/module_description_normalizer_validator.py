"""
Normalized Module Description Validator

Validates NormalizedModuleDescription objects after normalization.

The validator checks:

- required identity fields
- normalized textual fields
- structured values
- consistency between textual and structured values
- provenance preservation

The validator does not modify the data.
"""

import re
from dataclasses import fields

from src.etl.models.normalized_module_description import (
    NormalizedModuleDescription,
)
from src.etl.models.source import SourceRange

# ============================================================
# REQUIRED FIELDS
# ============================================================

REQUIRED_FIELDS = {
    "module_code",
    "module_name",
    "category",
}


# ============================================================
# TEXT FIELDS
# ============================================================

TEXT_FIELDS = {
    "module_code",
    "module_name",
    "category",
    "version",
    "responsible",
    "content",
    "qualification_goals",
    "teaching_forms",
    "prerequisites",
    "applicability",
    "credit_requirements",
    "examination",
    "credits_and_grades",
    "frequency",
    "workload",
    "duration",
    
}


# ============================================================
# STRUCTURED FIELDS
# ============================================================

STRUCTURED_FIELDS = {
    "credits",
    "workload_as",
    "duration_semesters",
}


# ============================================================
# VALIDATE SINGLE MODULE
# ============================================================

def validate_normalized_module(
    module: NormalizedModuleDescription,
) -> list[str]:

    problems: list[str] = []

    # --------------------------------------------------------
    # Required identity fields
    # --------------------------------------------------------

    for field_name in REQUIRED_FIELDS:

        value = getattr(
            module,
            field_name,
            None,
        )

        if value is None or not str(value).strip():

            problems.append(
                f"Missing required field: {field_name}"
            )

    # --------------------------------------------------------
    # Text field validation
    # --------------------------------------------------------

    for field_name in TEXT_FIELDS:

        value = getattr(
            module,
            field_name,
            None,
        )

        if value is None:
            continue

        if not isinstance(value, str):

            problems.append(
                f"{field_name} has unexpected type: "
                f"{type(value).__name__}"
            )

            continue

        # Leading whitespace
        if value != value.lstrip():

            problems.append(
                f"{field_name} contains leading whitespace"
            )

        # Trailing whitespace
        if value != value.rstrip():

            problems.append(
                f"{field_name} contains trailing whitespace"
            )

        # Carriage returns
        if "\r" in value:

            problems.append(
                f"{field_name} contains carriage returns"
            )

        # Excessive blank lines
        if "\n\n\n" in value:

            problems.append(
                f"{field_name} contains excessive blank lines"
            )

    # --------------------------------------------------------
    # Structured field types
    # --------------------------------------------------------

    for field_name in STRUCTURED_FIELDS:

        value = getattr(
            module,
            field_name,
            None,
        )

        if value is None:
            continue

        if not isinstance(value, int):

            problems.append(
                f"{field_name} has unexpected type: "
                f"{type(value).__name__}"
            )

            continue

        if value < 0:

            problems.append(
                f"{field_name} cannot be negative"
            )

    # --------------------------------------------------------
    # Credits consistency
    # --------------------------------------------------------

    if module.credits is not None:

        if module.credits <= 0:

            problems.append(
                "credits must be greater than zero"
            )

        if module.credits_and_grades:

            match = re.search(
                r"(\d+)\s+Leistungspunkte",
                module.credits_and_grades,
                re.IGNORECASE,
            )

            if match:

                textual_credits = int(
                    match.group(1)
                )

                if textual_credits != module.credits:

                    problems.append(
                        "credits does not match "
                        "credits_and_grades"
                    )

    # --------------------------------------------------------
    # Workload consistency
    # --------------------------------------------------------

    if module.workload_as is not None:

        if module.workload_as <= 0:

            problems.append(
                "workload_as must be greater than zero"
            )

        if module.workload:

            match = re.search(
                r"(\d+)\s*AS",
                module.workload,
                re.IGNORECASE,
            )

            if match:

                textual_workload = int(
                    match.group(1)
                )

                if textual_workload != module.workload_as:

                    problems.append(
                        "workload_as does not match "
                        "workload"
                    )

    # --------------------------------------------------------
    # Duration consistency
    # --------------------------------------------------------

    if module.duration_semesters is not None:

        if module.duration_semesters <= 0:

            problems.append(
                "duration_semesters must be greater "
                "than zero"
            )




    # --------------------------------------------------------
    # Provenance validation
    # --------------------------------------------------------

    if module.source is not None:

        if not isinstance(
            module.source,
            SourceRange,
        ):

            problems.append(
                "source has unexpected type: "
                f"{type(module.source).__name__}"
            )
    return problems


# ============================================================
# VALIDATE ALL MODULES
# ============================================================

def validate_normalized_modules(
    modules: list[NormalizedModuleDescription],
) -> dict[str, list[str]]:

    results: dict[str, list[str]] = {}

    for module in modules:

        problems = validate_normalized_module(
            module
        )

        if problems:

            module_code = (
                module.module_code
                or "<unknown>"
            )

            results[module_code] = problems

    return results


# ============================================================
# PRINT VALIDATION REPORT
# ============================================================

def print_normalized_validation_report(
    modules: list[NormalizedModuleDescription],
) -> None:

    results = validate_normalized_modules(
        modules
    )

    print()
    print("=" * 80)
    print("NORMALIZED MODULE DESCRIPTION VALIDATION")
    print("=" * 80)

    print(
        f"Normalized module descriptions: "
        f"{len(modules)}"
    )

    if not results:

        print()
        print(
            "All normalized modules passed validation."
        )

        return

    print()
    print(
        f"Modules with problems: "
        f"{len(results)}"
    )

    print()

    for module_code, problems in results.items():

        print("-" * 80)

        print(
            f"Module: {module_code}"
        )

        for problem in problems:

            print(
                f"  [!] {problem}"
            )