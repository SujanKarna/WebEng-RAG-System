"""
Module Description Validator

Validates parsed ModuleDescription objects and reports
structural extraction problems without modifying the data.
"""

from dataclasses import fields
import re
from src.etl.models.module_description import ModuleDescription


# ============================================================
# REQUIRED FIELDS
# ============================================================

REQUIRED_FIELDS = {
    "module_code",
    "module_name",
    "category",
}


# ============================================================
# FIELD HEADINGS
#
# Each heading belongs to exactly one parsed field.
#
# A field is allowed to contain its own heading because the
# parser may intentionally preserve the original section heading.
# A heading belonging to another field indicates possible
# extraction contamination.
# ============================================================

FIELD_HEADINGS = {
    "content": {
        "Inhalte",
    },
    "qualification_goals": {
        "Qualifikationsziele",
    },
    "teaching_forms": {
        "Lehrformen",
    },
    "prerequisites": {
        "Voraussetzungen für die Teilnahme",
    },
    "applicability": {
        "Verwendbarkeit des Moduls",
    },
    "credit_requirements": {
        "Voraussetzungen für die Vergabe von Leistungspunkten",
    },
    "examination": {
        "Modulprüfung",
    },
    "credits_and_grades": {
        "Leistungspunkte und Noten",
    },
    "frequency": {
        "Häufigkeit des Angebots",
    },
    "workload": {
        "Arbeitsaufwand",
    },
    "duration": {
        "Dauer des Moduls",
    },
}



def contains_structural_heading(
    text: str,
    heading: str,
) -> bool:
    """
    Detect whether a field heading appears as a standalone
    structural heading rather than merely being mentioned
    inside normal prose.
    """

    pattern = rf"(?m)^\s*{re.escape(heading)}\s*:?\s*$"

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None



# ============================================================
# REVERSE HEADING LOOKUP
# ============================================================

HEADING_TO_FIELD = {
    heading: field_name
    for field_name, headings in FIELD_HEADINGS.items()
    for heading in headings
}


# ============================================================
# VALIDATION RESULT
# ============================================================

def validate_module(
    module: ModuleDescription,
) -> list[str]:

    problems: list[str] = []

    # --------------------------------------------------------
    # Required fields
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
    # Cross-field structural heading contamination
    #
    # We only report a heading when it appears as an actual
    # standalone heading.
    #
    # Example that is VALID:
    #
    #   Die erfolgreiche Ablegung der Modulprüfung ist
    #   Voraussetzung für die Vergabe von Leistungspunkten.
    #
    # Example that is INVALID:
    #
    #   Die erfolgreiche Ablegung der Modulprüfung ...
    #
    #   Modulprüfung
    #   Die Modulprüfung besteht aus ...
    # --------------------------------------------------------

    ignored_fields = {
        "source",
        "module_code",
        "module_name",
        "category",
        "version",
    }

    for field in fields(module):

        field_name = field.name

        if field_name in ignored_fields:
            continue

        value = getattr(
            module,
            field_name,
            None,
        )

        if not value:
            continue

        value_text = str(value)

        for heading, owner_field in HEADING_TO_FIELD.items():

            # A field is allowed to contain its own heading.
            if owner_field == field_name:
                continue

            if contains_structural_heading(
                value_text,
                heading,
            ):
                problems.append(
                    f"{field_name} contains structural "
                    f"heading '{heading}' belonging to "
                    f"'{owner_field}'"
                )

    return problems


# ============================================================
# VALIDATE ALL MODULES
# ============================================================

def validate_modules(
    modules: list[ModuleDescription],
) -> dict[str, list[str]]:

    results: dict[str, list[str]] = {}

    for module in modules:

        problems = validate_module(
            module
        )

        if problems:

            results[
                module.module_code
            ] = problems

    return results


# ============================================================
# PRINT VALIDATION REPORT
# ============================================================

def print_validation_report(
    modules: list[ModuleDescription],
) -> None:

    results = validate_modules(
        modules
    )

    print()
    print("=" * 80)
    print("MODULE DESCRIPTION VALIDATION")
    print("=" * 80)

    if not results:

        print(
            "All modules passed validation."
        )

        return

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