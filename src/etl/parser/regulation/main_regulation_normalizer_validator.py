class MainRegulationValidator:

    EXPECTED_TOTAL_CREDITS = 120

    EXPECTED_SECTIONS = {
        "1": "Grundlagenmodule",
        "2": "Vertiefungsmodule",
        "3": "Module Schlüsselkompetenzen",
        "4": "Modul Forschungsseminar",
        "5": "Challengemodule",
        "6": "Modul Master-Arbeit",
    }

    EXPECTED_SECTION_CREDITS = {
        "1": 15,
        "2": 10,
        "3": 15,
        "4": 5,
        "5": 45,
        "6": 30,
    }

    # ========================================================
    # Public API
    # ========================================================

    def validate(self, regulation):

        errors = []
        warnings = []

        if not isinstance(regulation, list):
            errors.append(
                "Main regulation must be a list."
            )
            return errors, warnings

        self._validate_paragraphs(
            regulation,
            errors,
            warnings,
        )

        self._validate_section_6(
            regulation,
            errors,
            warnings,
        )

        self._validate_section_6_credits(
            regulation,
            errors,
            warnings,
        )

        self._validate_total_credits(
            regulation,
            errors,
            warnings,
        )

        return errors, warnings

    # ========================================================
    # Paragraph validation
    # ========================================================

    def _validate_paragraphs(
        self,
        regulation,
        errors,
        warnings,
    ):

        for index, paragraph in enumerate(regulation):

            if not isinstance(paragraph, dict):
                errors.append(
                    f"Paragraph {index} is not a dictionary."
                )
                continue

            if not paragraph.get("paragraph"):
                errors.append(
                    f"Paragraph {index} has no paragraph number."
                )

            if not paragraph.get("paragraph_title"):
                warnings.append(
                    f"{paragraph.get('paragraph')}: "
                    f"missing paragraph title."
                )

            if not paragraph.get("text"):
                warnings.append(
                    f"{paragraph.get('paragraph')}: "
                    f"empty text."
                )

    # ========================================================
    # §6 validation
    # ========================================================

    def _validate_section_6(
        self,
        regulation,
        errors,
        warnings,
    ):

        section_6 = next(
            (
                paragraph
                for paragraph in regulation
                if paragraph.get("paragraph") == "§ 6"
            ),
            None,
        )

        if section_6 is None:
            errors.append(
                "§ 6 was not found."
            )
            return

        sections = section_6.get(
            "sections",
            [],
        )

        if not sections:
            errors.append(
                "§ 6 contains no structured sections."
            )
            return

        found_numbers = set()

        for section in sections:

            if not isinstance(section, dict):
                errors.append(
                    "§6 contains a section that is not "
                    "a dictionary."
                )
                continue

            number = section.get(
                "number"
            )

            title = section.get(
                "title"
            )

            found_numbers.add(number)

            if number not in self.EXPECTED_SECTIONS:
                warnings.append(
                    f"§6: unexpected section number "
                    f"'{number}'."
                )

            if (
                number in self.EXPECTED_SECTIONS
                and title != self.EXPECTED_SECTIONS[number]
            ):
                warnings.append(
                    f"§6 section {number}: "
                    f"expected title "
                    f"'{self.EXPECTED_SECTIONS[number]}', "
                    f"got '{title}'."
                )

            self._validate_modules(
                section,
                errors,
                warnings,
            )

            self._validate_selection(
                section,
                errors,
                warnings,
            )

            self._validate_selection_groups(
                section,
                errors,
                warnings,
            )

            self._validate_conditional_modules(
                section,
                errors,
                warnings,
            )

        missing = (
            set(self.EXPECTED_SECTIONS)
            - found_numbers
        )

        for number in sorted(missing):
            errors.append(
                f"§6: missing section {number} "
                f"({self.EXPECTED_SECTIONS[number]})."
            )

    # ========================================================
    # Modules
    # ========================================================

    def _validate_modules(
        self,
        section,
        errors,
        warnings,
    ):

        modules = section.get(
            "modules",
            []
        )

        if not isinstance(modules, list):
            errors.append(
                f"§6 section {section.get('number')}: "
                f"'modules' must be a list."
            )
            return

        for index, module in enumerate(modules):

            self._validate_module(
                module,
                f"§6 section "
                f"{section.get('number')} "
                f"module {index}",
                errors,
                warnings,
            )

    # ========================================================
    # Single module
    # ========================================================

    def _validate_module(
        self,
        module,
        context,
        errors,
        warnings,
    ):

        if not isinstance(module, dict):
            errors.append(
                f"{context}: module is not a dictionary."
            )
            return

        code = module.get(
            "module_code"
        )

        name = module.get(
            "module_name"
        )

        credits = module.get(
            "credits"
        )

        requirement = module.get(
            "requirement"
        )

        if not code:
            errors.append(
                f"{context}: missing module_code."
            )

        elif not isinstance(code, str):
            errors.append(
                f"{context}: module_code must be a string."
            )

        if not name:
            errors.append(
                f"{context}: missing module_name."
            )

        elif not isinstance(name, str):
            errors.append(
                f"{context}: module_name must be a string."
            )

        if credits is None:
            errors.append(
                f"{context}: missing credits."
            )

        elif not isinstance(credits, int):
            errors.append(
                f"{context}: credits must be int."
            )

        elif credits <= 0:
            errors.append(
                f"{context}: credits must be greater than 0."
            )

        if not requirement:
            warnings.append(
                f"{context}: missing requirement."
            )

    # ========================================================
    # Selection
    # ========================================================

    def _validate_selection(
        self,
        section,
        errors,
        warnings,
    ):

        selection = section.get(
            "selection"
        )

        if not selection:
            return

        if not isinstance(selection, dict):
            errors.append(
                f"§6 section {section.get('number')}: "
                f"'selection' must be a dictionary."
            )
            return

        selection_type = selection.get(
            "type"
        )

        valid_types = {
            "minimum_credits",
            "mandatory",
        }

        if selection_type not in valid_types:
            errors.append(
                f"§6 section {section.get('number')}: "
                f"invalid selection type "
                f"'{selection_type}'."
            )

        if selection_type == "minimum_credits":

            credits = selection.get(
                "credits"
            )

            if not isinstance(
                credits,
                int,
            ):
                errors.append(
                    f"§6 section {section.get('number')}: "
                    f"minimum_credits requires integer "
                    f"'credits'."
                )

            elif credits <= 0:
                errors.append(
                    f"§6 section {section.get('number')}: "
                    f"minimum credits must be greater "
                    f"than 0."
                )

        if selection_type == "mandatory":

            if "credits" in selection:
                credits = selection.get(
                    "credits"
                )

                if not isinstance(
                    credits,
                    int,
                ):
                    errors.append(
                        f"§6 section {section.get('number')}: "
                        f"mandatory selection credits "
                        f"must be integer."
                    )

    # ========================================================
    # Selection groups
    # ========================================================

    def _validate_selection_groups(
        self,
        section,
        errors,
        warnings,
    ):

        groups = section.get(
            "selection_groups",
            []
        )

        if not isinstance(groups, list):
            errors.append(
                f"§6 section {section.get('number')}: "
                f"'selection_groups' must be a list."
            )
            return

        for index, group in enumerate(groups):

            if not isinstance(group, dict):
                errors.append(
                    f"§6 section {section.get('number')} "
                    f"selection group {index}: "
                    f"group is not a dictionary."
                )
                continue

            selection_type = group.get(
                "selection_type"
            )

            if selection_type != "exactly_one":
                errors.append(
                    f"§6 section {section.get('number')} "
                    f"selection group {index}: "
                    f"invalid selection_type "
                    f"'{selection_type}'."
                )

            modules = group.get(
                "modules",
                []
            )

            if not modules:
                errors.append(
                    f"§6 section {section.get('number')} "
                    f"selection group {index}: "
                    f"contains no modules."
                )
                continue

            if not isinstance(modules, list):
                errors.append(
                    f"§6 section {section.get('number')} "
                    f"selection group {index}: "
                    f"'modules' must be a list."
                )
                continue

            for module_index, module in enumerate(
                modules
            ):

                self._validate_module(
                    module,
                    (
                        f"§6 section "
                        f"{section.get('number')} "
                        f"selection group "
                        f"{index} module "
                        f"{module_index}"
                    ),
                    errors,
                    warnings,
                )

    # ========================================================
    # Conditional modules
    # ========================================================

    def _validate_conditional_modules(
        self,
        section,
        errors,
        warnings,
    ):

        conditional_modules = section.get(
            "conditional_modules",
            []
        )

        if not isinstance(
            conditional_modules,
            list,
        ):
            errors.append(
                f"§6 section {section.get('number')}: "
                f"'conditional_modules' must be a list."
            )
            return

        for index, conditional in enumerate(
            conditional_modules
        ):

            if not isinstance(
                conditional,
                dict,
            ):
                errors.append(
                    f"§6 section {section.get('number')} "
                    f"conditional module {index}: "
                    f"conditional module must be "
                    f"a dictionary."
                )
                continue

            condition = conditional.get(
                "condition"
            )

            module = conditional.get(
                "module"
            )

            if not condition:
                errors.append(
                    f"§6 section {section.get('number')} "
                    f"conditional module {index}: "
                    f"missing condition."
                )

            if not module:
                errors.append(
                    f"§6 section {section.get('number')} "
                    f"conditional module {index}: "
                    f"missing module."
                )
                continue

            self._validate_module(
                module,
                (
                    f"§6 section "
                    f"{section.get('number')} "
                    f"conditional module "
                    f"{index}"
                ),
                errors,
                warnings,
            )

    # ========================================================
    # §6 CREDIT VALIDATION
    # ========================================================

    def _validate_section_6_credits(
        self,
        regulation,
        errors,
        warnings,
    ):

        section_6 = next(
            (
                paragraph
                for paragraph in regulation
                if paragraph.get("paragraph") == "§ 6"
            ),
            None,
        )

        if section_6 is None:
            return

        sections = section_6.get(
            "sections",
            []
        )

        section_map = {
            section.get("number"): section
            for section in sections
            if isinstance(section, dict)
        }

        # ----------------------------------------------------
        # 1. Grundlagenmodule = 15 LP
        # ----------------------------------------------------

        self._validate_minimum_selection_credits(
            section_map.get("1"),
            expected_credits=15,
            errors=errors,
            warnings=warnings,
        )

        # ----------------------------------------------------
        # 2. Vertiefungsmodule = 10 LP
        # ----------------------------------------------------

        self._validate_minimum_selection_credits(
            section_map.get("2"),
            expected_credits=10,
            errors=errors,
            warnings=warnings,
        )

        # ----------------------------------------------------
        # 3. Schlüsselkompetenzen = 15 LP
        # ----------------------------------------------------

        self._validate_minimum_selection_credits(
            section_map.get("3"),
            expected_credits=15,
            errors=errors,
            warnings=warnings,
        )

        # ----------------------------------------------------
        # 4. Forschungsseminar = 5 LP
        # ----------------------------------------------------

        self._validate_mandatory_module_credits(
            section_map.get("4"),
            expected_credits=5,
            errors=errors,
            warnings=warnings,
        )

        # ----------------------------------------------------
        # 5. Challengemodule
        #
        # Team Challenge = 15 LP
        # Startup / International = exactly one × 30 LP
        # ----------------------------------------------------

        section_5 = section_map.get("5")

        if section_5 is not None:

            self._validate_challenge_section(
                section_5,
                errors,
                warnings,
            )

        # ----------------------------------------------------
        # 6. Master-Arbeit = 30 LP
        # ----------------------------------------------------

        self._validate_mandatory_module_credits(
            section_map.get("6"),
            expected_credits=30,
            errors=errors,
            warnings=warnings,
        )

    # ========================================================
    # Minimum credit selection
    # ========================================================

    def _validate_minimum_selection_credits(
        self,
        section,
        expected_credits,
        errors,
        warnings,
    ):

        if section is None:
            return

        selection = section.get(
            "selection"
        )

        if not selection:
            errors.append(
                f"§6 section {section.get('number')}: "
                f"missing selection information."
            )
            return

        selection_type = selection.get(
            "type"
        )

        if selection_type != "minimum_credits":
            errors.append(
                f"§6 section {section.get('number')}: "
                f"expected selection type "
                f"'minimum_credits', "
                f"got '{selection_type}'."
            )
            return

        actual = selection.get(
            "credits"
        )

        if actual != expected_credits:
            errors.append(
                f"§6 section {section.get('number')}: "
                f"expected selection of "
                f"{expected_credits} LP, "
                f"got {actual} LP."
            )

    # ========================================================
    # Mandatory module credit validation
    # ========================================================

    def _validate_mandatory_module_credits(
        self,
        section,
        expected_credits,
        errors,
        warnings,
    ):

        if section is None:
            return

        modules = section.get(
            "modules",
            []
        )

        if not isinstance(modules, list):
            return

        if len(modules) != 1:
            errors.append(
                f"§6 section {section.get('number')}: "
                f"expected exactly one mandatory module, "
                f"found {len(modules)}."
            )
            return

        module = modules[0]

        if module.get(
            "credits"
        ) != expected_credits:

            errors.append(
                f"§6 section {section.get('number')}: "
                f"expected {expected_credits} LP, "
                f"got {module.get('credits')} LP."
            )

        if module.get(
            "requirement"
        ) != "Pflichtmodul":

            errors.append(
                f"§6 section {section.get('number')}: "
                f"module {module.get('module_code')} "
                f"must be a Pflichtmodul."
            )

    # ========================================================
    # Challenge section validation
    # ========================================================

    def _validate_challenge_section(
        self,
        section,
        errors,
        warnings,
    ):

        # ----------------------------------------------------
        # Team Challenge
        # ----------------------------------------------------

        modules = section.get(
            "modules",
            []
        )

        team_modules = [
            module
            for module in modules
            if module.get("module_code")
            == "255030-009"
        ]

        if len(team_modules) != 1:

            errors.append(
                "§6 section 5: "
                "expected exactly one Team Challenge "
                "(255030-009)."
            )

        else:

            team = team_modules[0]

            if team.get("credits") != 15:
                errors.append(
                    "§6 section 5: "
                    "Team Challenge "
                    "(255030-009) must have 15 LP."
                )

            if team.get(
                "requirement"
            ) != "Pflichtmodul":

                errors.append(
                    "§6 section 5: "
                    "Team Challenge "
                    "(255030-009) must be "
                    "a Pflichtmodul."
                )

        # ----------------------------------------------------
        # Startup / International Experience
        # ----------------------------------------------------

        groups = section.get(
            "selection_groups",
            []
        )

        if len(groups) != 1:

            errors.append(
                "§6 section 5: "
                "expected exactly one challenge "
                "selection group."
            )

            return

        group = groups[0]

        if group.get(
            "selection_type"
        ) != "exactly_one":

            errors.append(
                "§6 section 5: "
                "challenge selection group "
                "must use 'exactly_one'."
            )

        modules = group.get(
            "modules",
            []
        )

        expected_codes = {
            "255030-010",
            "255030-011",
        }

        actual_codes = {
            module.get("module_code")
            for module in modules
        }

        if actual_codes != expected_codes:

            errors.append(
                "§6 section 5: "
                "challenge selection group must "
                "contain exactly "
                "Startup Experience "
                "(255030-010) and "
                "International Experience "
                "(255030-011)."
            )

        if len(modules) != 2:

            errors.append(
                "§6 section 5: "
                "challenge selection group must "
                "contain exactly two modules."
            )

        for module in modules:

            code = module.get(
                "module_code"
            )

            credits = module.get(
                "credits"
            )

            requirement = module.get(
                "requirement"
            )

            if credits != 30:

                errors.append(
                    f"§6 section 5: "
                    f"{code} must have 30 LP, "
                    f"got {credits} LP."
                )

            if requirement != "Wahlpflichtmodul":

                warnings.append(
                    f"§6 section 5: "
                    f"{code} is expected to be "
                    f"a Wahlpflichtmodul."
                )

    # ========================================================
    # TOTAL 120 LP VALIDATION
    # ========================================================

    def _validate_total_credits(
        self,
        regulation,
        errors,
        warnings,
    ):

        section_6 = next(
            (
                paragraph
                for paragraph in regulation
                if paragraph.get("paragraph") == "§ 6"
            ),
            None,
        )

        if section_6 is None:
            return

        sections = section_6.get(
            "sections",
            []
        )

        section_map = {
            section.get("number"): section
            for section in sections
            if isinstance(section, dict)
        }

        total = 0

        # ----------------------------------------------------
        # 1. Grundlagenmodule
        #
        # Student selects 15 LP.
        # ----------------------------------------------------

        section = section_map.get("1")

        if section:

            selection = section.get(
                "selection",
                {}
            )

            if (
                selection.get("type")
                == "minimum_credits"
            ):

                total += selection.get(
                    "credits",
                    0
                )

        # ----------------------------------------------------
        # 2. Vertiefungsmodule
        #
        # Student selects 10 LP.
        # ----------------------------------------------------

        section = section_map.get("2")

        if section:

            selection = section.get(
                "selection",
                {}
            )

            if (
                selection.get("type")
                == "minimum_credits"
            ):

                total += selection.get(
                    "credits",
                    0
                )

        # ----------------------------------------------------
        # 3. Schlüsselkompetenzen
        #
        # Student selects 15 LP.
        #
        # Conditional German modules are NOT added here
        # because they are part of this 15 LP category.
        # ----------------------------------------------------

        section = section_map.get("3")

        if section:

            selection = section.get(
                "selection",
                {}
            )

            if (
                selection.get("type")
                == "minimum_credits"
            ):

                total += selection.get(
                    "credits",
                    0
                )

        # ----------------------------------------------------
        # 4. Forschungsseminar
        # ----------------------------------------------------

        section = section_map.get("4")

        if section:

            for module in section.get(
                "modules",
                []
            ):

                if (
                    module.get("module_code")
                    == "250000-019"
                ):

                    total += module.get(
                        "credits",
                        0
                    )

        # ----------------------------------------------------
        # 5. Challengemodule
        #
        # Team Challenge = 15 LP
        # exactly one of the two 30 LP modules = 30 LP
        # ----------------------------------------------------

        section = section_map.get("5")

        if section:

            for module in section.get(
                "modules",
                []
            ):

                if (
                    module.get("module_code")
                    == "255030-009"
                ):

                    total += module.get(
                        "credits",
                        0
                    )

            groups = section.get(
                "selection_groups",
                []
            )

            for group in groups:

                if (
                    group.get("selection_type")
                    == "exactly_one"
                ):

                    modules = group.get(
                        "modules",
                        []
                    )

                    if modules:

                        # All challenge alternatives are
                        # expected to be 30 LP.
                        total += modules[0].get(
                            "credits",
                            0
                        )

        # ----------------------------------------------------
        # 6. Master-Arbeit
        # ----------------------------------------------------

        section = section_map.get("6")

        if section:

            for module in section.get(
                "modules",
                []
            ):

                if (
                    module.get("module_code")
                    == "250000-911"
                ):

                    total += module.get(
                        "credits",
                        0
                    )

        # ----------------------------------------------------
        # Final check
        # ----------------------------------------------------

        if total != self.EXPECTED_TOTAL_CREDITS:

            errors.append(
                f"§6: expected total degree credits "
                f"of {self.EXPECTED_TOTAL_CREDITS} LP, "
                f"calculated {total} LP."
            )

    # ========================================================
    # Report
    # ========================================================


def print_normalized_main_regulation_validation_report(
    regulation
):

    validator = MainRegulationValidator()

    errors, warnings = validator.validate(
        regulation
    )

    print()
    print("-" * 80)
    print("MAIN REGULATION VALIDATION REPORT")
    print("-" * 80)

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
            "✓ Main regulation validation passed."
        )

    return not errors