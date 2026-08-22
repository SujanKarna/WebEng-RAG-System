"""
Module Description Validator

Validates parsed ModuleDescription objects and reports
structural extraction problems without modifying the data.
"""

from dataclasses import fields

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
# FIELD LABELS THAT SHOULD NEVER APPEAR INSIDE A VALUE
# ============================================================

FIELD_LABELS = [
    "Modulnummer",
    "Modulname",
    "Modulverantwortlich",
    "Inhalte und Qualifikationsziele",
    "Inhalte",
    "Qualifikationsziele",
    "Lehrformen",
    "Voraussetzungen für die Teilnahme",
    "Verwendbarkeit des Moduls",
    "Voraussetzungen für die Vergabe von Leistungspunkten",
    "Modulprüfung",
    "Leistungspunkte und Noten",
    "Häufigkeit des Angebots",
    "Arbeitsaufwand",
    "Dauer des Moduls",
]


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
    # Check suspicious field contamination
    # --------------------------------------------------------

    for field in fields(module):

        field_name = field.name

        if field_name in {
            "source",
            "module_code",
            "module_name",
            "category",
            "version",
        }:
            continue

        value = getattr(
            module,
            field_name,
            None,
        )

        if not value:
            continue

        value_text = str(value)

        for label in FIELD_LABELS:

            if label.lower() in value_text.lower():

                problems.append(
                    f"{field_name} contains field heading "
                    f"'{label}'"
                )

    # --------------------------------------------------------
    # Content checks
    # --------------------------------------------------------

    if module.content:

        if "Qualifikationsziele" in module.content:

            problems.append(
                "content contains "
                "'Qualifikationsziele'"
            )

    if module.qualification_goals:

        if "Lehrformen" in module.qualification_goals:

            problems.append(
                "qualification_goals contains "
                "'Lehrformen'"
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