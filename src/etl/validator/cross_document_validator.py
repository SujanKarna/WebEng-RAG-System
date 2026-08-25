import json
from pathlib import Path
from collections import Counter


class CrossDocumentValidator:
    """
    Validates the relationship between the persisted normalized
    main regulation and persisted normalized module descriptions.

    IMPORTANT:
    This validator works ONLY with the persisted JSON files.
    It does not depend on parser/normalizer Python objects.
    """

    def __init__(
        self,
        main_regulation_path,
        module_descriptions_path,
    ):

        self.main_regulation_path = Path(
            main_regulation_path
        )

        self.module_descriptions_path = Path(
            module_descriptions_path
        )

    # ========================================================
    # PUBLIC
    # ========================================================

    def validate(self):

        errors = []
        warnings = []

        main_regulation = self._load_json(
            self.main_regulation_path,
            errors,
            "main regulation",
        )

        module_descriptions = self._load_json(
            self.module_descriptions_path,
            errors,
            "module descriptions",
        )

        if errors:
            return errors, warnings

        # ----------------------------------------------------
        # Extract canonical module information
        # ----------------------------------------------------

        regulation_modules = (
            self._extract_regulation_modules(
                main_regulation,
                errors,
                warnings,
            )
        )

        description_modules = (
            self._extract_description_modules(
                module_descriptions,
                errors,
                warnings,
            )
        )

        # ----------------------------------------------------
        # Duplicate detection
        # ----------------------------------------------------

        self._validate_duplicate_codes(
            regulation_modules,
            "main regulation",
            errors,
            warnings,
        )

        self._validate_duplicate_codes(
            description_modules,
            "module descriptions",
            errors,
            warnings,
        )

        # ----------------------------------------------------
        # Cross-document comparison
        # ----------------------------------------------------

        self._validate_module_references(
            regulation_modules,
            description_modules,
            errors,
            warnings,
        )

        self._validate_unreferenced_descriptions(
            regulation_modules,
            description_modules,
            errors,
            warnings,
        )

        self._validate_module_metadata(
            regulation_modules,
            description_modules,
            errors,
            warnings,
        )

        # ----------------------------------------------------
        # Curriculum total
        # ----------------------------------------------------

        self._validate_curriculum_total(
            regulation_modules,
            errors,
            warnings,
        )

        return errors, warnings

    # ========================================================
    # JSON LOADING
    # ========================================================

    def _load_json(
        self,
        path,
        errors,
        label,
    ):

        if not path.exists():

            errors.append(
                f"{label} file does not exist: {path}"
            )

            return None

        try:

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except json.JSONDecodeError as exc:

            errors.append(
                f"{label} JSON could not be decoded: "
                f"{exc}"
            )

        except OSError as exc:

            errors.append(
                f"Could not read {label} file: "
                f"{exc}"
            )

        return None

    # ========================================================
    # MAIN REGULATION MODULE EXTRACTION
    # ========================================================

    def _extract_regulation_modules(
        self,
        regulation,
        errors,
        warnings,
    ):

        modules = []

        if not isinstance(regulation, list):

            errors.append(
                "Normalized main regulation must be a list."
            )

            return modules

        section_6 = next(
            (
                paragraph
                for paragraph in regulation
                if isinstance(paragraph, dict)
                and paragraph.get("paragraph") == "§ 6"
            ),
            None,
        )

        if section_6 is None:

            errors.append(
                "§ 6 was not found in normalized "
                "main regulation."
            )

            return modules

        sections = section_6.get(
            "sections",
            [],
        )

        if not isinstance(sections, list):

            errors.append(
                "§ 6 sections must be a list."
            )

            return modules

        for section in sections:

            if not isinstance(section, dict):
                continue

            # ------------------------------------------------
            # Normal modules
            # ------------------------------------------------

            for module in section.get(
                "modules",
                [],
            ):

                if isinstance(module, dict):

                    modules.append(module)

            # ------------------------------------------------
            # Selection groups
            # ------------------------------------------------

            for group in section.get(
                "selection_groups",
                [],
            ):

                if not isinstance(group, dict):
                    continue

                for module in group.get(
                    "modules",
                    [],
                ):

                    if isinstance(module, dict):

                        modules.append(module)

            # ------------------------------------------------
            # Conditional modules
            # ------------------------------------------------

            for conditional in section.get(
                "conditional_modules",
                [],
            ):

                if not isinstance(
                    conditional,
                    dict,
                ):
                    continue

                module = conditional.get(
                    "module"
                )

                if isinstance(module, dict):

                    modules.append(module)

        return modules

    # ========================================================
    # MODULE DESCRIPTION EXTRACTION
    # ========================================================

    def _extract_description_modules(
        self,
        descriptions,
        errors,
        warnings,
    ):

        modules = []

        if not isinstance(
            descriptions,
            list,
        ):

            errors.append(
                "Normalized module descriptions "
                "must be a list."
            )

            return modules

        for index, module in enumerate(
            descriptions
        ):

            if not isinstance(
                module,
                dict,
            ):

                errors.append(
                    f"Module description {index} "
                    f"is not a dictionary."
                )

                continue

            modules.append(module)

        return modules

    # ========================================================
    # DUPLICATES
    # ========================================================

    def _validate_duplicate_codes(
        self,
        modules,
        source,
        errors,
        warnings,
    ):

        codes = []

        for module in modules:

            code = self._module_code(
                module
            )

            if code:
                codes.append(code)

        counts = Counter(codes)

        for code, count in counts.items():

            if count > 1:

                errors.append(
                    f"Duplicate module code '{code}' "
                    f"found {count} times in "
                    f"{source}."
                )

    # ========================================================
    # MODULE REFERENCES
    # ========================================================

    def _validate_module_references(
        self,
        regulation_modules,
        description_modules,
        errors,
        warnings,
    ):

        description_codes = {
            self._module_code(module)
            for module in description_modules
            if self._module_code(module)
        }

        regulation_codes = {
            self._module_code(module)
            for module in regulation_modules
            if self._module_code(module)
        }

        for code in sorted(
            regulation_codes
            - description_codes
        ):

            warnings.append(
                f"Module '{code}' is referenced "
                f"in §6 but has no module description."
            )

    # ========================================================
    # UNREFERENCED DESCRIPTIONS
    # ========================================================

    def _validate_unreferenced_descriptions(
        self,
        regulation_modules,
        description_modules,
        errors,
        warnings,
    ):

        regulation_codes = {
            self._module_code(module)
            for module in regulation_modules
            if self._module_code(module)
        }

        description_codes = {
            self._module_code(module)
            for module in description_modules
            if self._module_code(module)
        }

        unreferenced = (
            description_codes
            - regulation_codes
        )

        if unreferenced:

            warnings.append(
                f"{len(unreferenced)} module descriptions "
                f"are not referenced in §6."
            )

            for code in sorted(
                unreferenced
            ):

                warnings.append(
                    f"Module description '{code}' "
                    f"is not referenced in §6."
                )

    # ========================================================
    # MODULE METADATA
    # ========================================================

    def _validate_module_metadata(
        self,
        regulation_modules,
        description_modules,
        errors,
        warnings,
    ):

        regulation_by_code = {}

        for module in regulation_modules:

            code = self._module_code(
                module
            )

            if code:
                regulation_by_code[code] = module

        descriptions_by_code = {}

        for module in description_modules:

            code = self._module_code(
                module
            )

            if code:
                descriptions_by_code[code] = module

        common_codes = (
            regulation_by_code.keys()
            & descriptions_by_code.keys()
        )

        for code in sorted(common_codes):

            regulation_module = (
                regulation_by_code[code]
            )

            description_module = (
                descriptions_by_code[code]
            )

            self._compare_names(
                code,
                regulation_module,
                description_module,
                warnings,
            )

            self._compare_credits(
                code,
                regulation_module,
                description_module,
                warnings,
            )

    # ========================================================
    # NAME COMPARISON
    # ========================================================

    def _compare_names(
        self,
        code,
        regulation_module,
        description_module,
        warnings,
    ):

        regulation_name = (
            regulation_module.get(
                "module_name"
            )
        )

        description_name = (
            description_module.get(
                "module_name"
            )
        )

        if not regulation_name:
            return

        if not description_name:
            return

        if (
            self._normalize_text(
                regulation_name
            )
            !=
            self._normalize_text(
                description_name
            )
        ):

            warnings.append(
                f"Module '{code}' name differs "
                f"between §6 and module description: "
                f"§6='{regulation_name}' | "
                f"description='{description_name}'."
            )

    # ========================================================
    # CREDIT COMPARISON
    # ========================================================

    def _compare_credits(
        self,
        code,
        regulation_module,
        description_module,
        warnings,
    ):

        regulation_credits = (
            regulation_module.get(
                "credits"
            )
        )

        description_credits = (
            description_module.get(
                "credits"
            )
        )

        if (
            regulation_credits is None
            or description_credits is None
        ):

            return

        if (
            regulation_credits
            !=
            description_credits
        ):

            warnings.append(
                f"Module '{code}' credits differ "
                f"between §6 and module description: "
                f"§6={regulation_credits} | "
                f"description={description_credits}."
            )

    # ========================================================
    # CURRICULUM TOTAL
    # ========================================================

    def _validate_curriculum_total(
        self,
        regulation_modules,
        errors,
        warnings,
    ):

        total = 0

        seen_codes = set()

        for module in regulation_modules:

            code = self._module_code(
                module
            )

            credits = module.get(
                "credits"
            )

            if not code:
                continue

            # Avoid counting the same module twice
            # if it appears through multiple structures.
            if code in seen_codes:
                continue

            if isinstance(
                credits,
                int,
            ):

                total += credits
                seen_codes.add(code)

        if total != 120:

            warnings.append(
                f"Curriculum credit total is "
                f"{total} LP instead of expected "
                f"120 LP."
            )

        else:

            warnings.append(
                "Curriculum credit total validated "
                "successfully: 120 LP."
            )

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _module_code(module):

        if not isinstance(
            module,
            dict,
        ):

            return None

        code = module.get(
            "module_code"
        )

        if code is None:
            return None

        return str(code).strip()

    @staticmethod
    def _normalize_text(value):

        return (
            str(value)
            .strip()
            .lower()
            .replace("–", "-")
            .replace("—", "-")
        )


# ============================================================
# PUBLIC HELPER
# ============================================================

def print_cross_document_validation_report(
    main_regulation_path,
    module_descriptions_path,
):

    validator = CrossDocumentValidator(
        main_regulation_path=main_regulation_path,
        module_descriptions_path=module_descriptions_path,
    )

    errors, warnings = (
        validator.validate()
    )

    print()
    print("=" * 80)
    print("CROSS-DOCUMENT VALIDATION")
    print("=" * 80)

    print(
        f"Main regulation modules: "
        f"{_count_regulation_modules(
            main_regulation_path
        )}"
    )

    print(
        f"Module descriptions: "
        f"{_count_module_descriptions(
            module_descriptions_path
        )}"
    )

    print(
        f"Errors:   {len(errors)}"
    )

    print(
        f"Warnings: {len(warnings)}"
    )

    if errors:

        print()
        print("ERRORS:")

        for error in errors:

            print(
                f"  [ERROR] {error}"
            )

    if warnings:

        print()
        print("WARNINGS:")

        for warning in warnings:

            print(
                f"  [WARNING] {warning}"
            )

    if not errors:

        print()
        print(
            "✓ Cross-document validation passed."
        )

    return not errors


# ============================================================
# Reporting helpers
# ============================================================

def _load_json_file(path):

    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def _count_regulation_modules(path):

    try:

        regulation = _load_json_file(path)

        validator = CrossDocumentValidator(
            path,
            path,
        )

        modules = (
            validator._extract_regulation_modules(
                regulation,
                [],
                [],
            )
        )

        codes = {
            validator._module_code(module)
            for module in modules
            if validator._module_code(module)
        }

        return len(codes)

    except Exception:

        return 0


def _count_module_descriptions(path):

    try:

        descriptions = _load_json_file(path)

        if not isinstance(
            descriptions,
            list,
        ):

            return 0

        codes = {
            str(module.get("module_code")).strip()
            for module in descriptions
            if isinstance(module, dict)
            and module.get("module_code")
        }

        return len(codes)

    except Exception:

        return 0

