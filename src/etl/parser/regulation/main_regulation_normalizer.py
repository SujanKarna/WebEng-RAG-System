import re


class MainRegulationNormalizer:

    MODULE_CODE_PATTERN = re.compile(
        r"(?P<code>\d{6}-\d{3})\s+"
        r"(?P<name>.+?),\s*"
        r"(?P<credits>\d+)\s+LP\s+"
        r"\((?P<requirement>[^)]+)\)"
    )

    SECTION_PATTERN = re.compile(
        r"(?m)(?P<number>[1-6])\.\s+"
        r"(?P<title>"
        r"Grundlagenmodule|"
        r"Vertiefungsmodule|"
        r"Module Schlüsselkompetenzen|"
        r"Modul Forschungsseminar|"
        r"Challengemodule|"
        r"Modul Master-Arbeit"
        r"):"
    )

    # ========================================================
    # PUBLIC API
    # ========================================================

    def normalize(self, regulation):

        normalized = []

        for paragraph in regulation:

            paragraph = dict(paragraph)

            # ------------------------------------------------
            # Normalize paragraph text
            # ------------------------------------------------

            paragraph["text"] = self._normalize_text(
                paragraph.get("text", "")
            )

            # ------------------------------------------------
            # Normalize blocks
            # ------------------------------------------------

            if "blocks" in paragraph:

                paragraph["blocks"] = [
                    self._normalize_block(block)
                    for block in paragraph["blocks"]
                ]

            # ------------------------------------------------
            # §6 contains structured study information
            # ------------------------------------------------

            if paragraph.get("paragraph") == "§ 6":

                paragraph = self._normalize_section_6(
                    paragraph
                )

            normalized.append(paragraph)

        return normalized

    # ========================================================
    # TEXT NORMALIZATION
    # ========================================================

    def _normalize_text(self, text):

        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # ----------------------------------------------------
        # PDF hyphenation
        #
        # Web-
        # Anwendungen
        #
        # ->
        #
        # Web-Anwendungen
        # ----------------------------------------------------

        text = re.sub(
            r"(?<=\w)-\n(?=\w)",
            "-",
            text,
        )

        # ----------------------------------------------------
        # Remaining line breaks are PDF wrapping
        # ----------------------------------------------------

        text = re.sub(
            r"\s*\n\s*",
            " ",
            text,
        )

        # ----------------------------------------------------
        # Collapse repeated whitespace
        # ----------------------------------------------------

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        return text.strip()

    # ========================================================
    # BLOCK NORMALIZATION
    # ========================================================

    def _normalize_block(self, block):

        normalized_block = dict(block)

        normalized_block["text"] = self._normalize_text(
            block.get("text", "")
        )

        return normalized_block

    # ========================================================
    # §6 NORMALIZATION
    # ========================================================

    def _normalize_section_6(self, paragraph):

        sections = paragraph.get("sections", [])

        # ----------------------------------------------------
        # If parser already created sections, normalize them.
        # ----------------------------------------------------

        if sections:

            paragraph["sections"] = [
                self._normalize_section(section)
                for section in sections
            ]

            return paragraph

        # ----------------------------------------------------
        # Parser did not create sections.
        #
        # Reconstruct them from the paragraph text.
        # ----------------------------------------------------

        text = paragraph.get("text", "")

        sections = self._parse_section_6_text(
            text
        )

        paragraph["sections"] = sections

        # ----------------------------------------------------
        # Extract paragraph (2) study progression
        # ----------------------------------------------------

        study_progression = self._extract_study_progression(
            text
        )

        if study_progression:

            paragraph["study_progression"] = (
                study_progression
            )

        return paragraph

    # ========================================================
    # PARSE §6 INTO SECTIONS
    # ========================================================

    def _parse_section_6_text(self, text):

        matches = list(
            self.SECTION_PATTERN.finditer(text)
        )

        sections = []

        for index, match in enumerate(matches):

            number = match.group("number")
            title = match.group("title")

            start = match.end()

            if index + 1 < len(matches):

                end = matches[index + 1].start()

            else:

                # Section 6 ends before paragraph (2).
                study_progression_match = re.search(
                    r"\(2\)\s+Der empfohlene Ablauf",
                    text[start:],
                )

                if study_progression_match:

                    end = (
                        start
                        + study_progression_match.start()
                    )

                else:

                    end = len(text)

            section_text = text[start:end].strip()

            section = self._build_section(
                number=number,
                title=title,
                text=section_text,
            )

            sections.append(section)

        return sections

    # ========================================================
    # BUILD SECTION
    # ========================================================

    def _build_section(
        self,
        number,
        title,
        text,
    ):

        section = {
            "number": number,
            "title": title,
            "text": text,
        }

        # ----------------------------------------------------
        # Section 1
        # ----------------------------------------------------

        if number == "1":

            modules = self._extract_modules(
                text
            )

            section["modules"] = modules

            section["selection"] = {
                "type": "minimum_credits",
                "credits": self._extract_selection_credits(
                    text
                ),
            }

        # ----------------------------------------------------
        # Section 2
        # ----------------------------------------------------

        elif number == "2":

            modules = self._extract_modules(
                text
            )

            section["modules"] = modules

            section["selection"] = {
                "type": "minimum_credits",
                "credits": self._extract_selection_credits(
                    text
                ),
            }

        # ----------------------------------------------------
        # Section 3
        # ----------------------------------------------------

        elif number == "3":

            modules = self._extract_modules(
                text
            )

            # ------------------------------------------------
            # Remove conditional German modules from the
            # normal module list.
            # ------------------------------------------------

            modules = [
                module
                for module in modules
                if module["module_code"]
                not in {
                    "136004-005",
                    "136004-006",
                }
            ]

            section["modules"] = modules

            section["selection"] = {
                "type": "minimum_credits",
                "credits": self._extract_selection_credits(
                    text
                ),
            }

            conditional_modules = (
                self._extract_conditional_modules(
                    text
                )
            )

            if conditional_modules:

                section["conditional_modules"] = (
                    conditional_modules
                )

        # ----------------------------------------------------
        # Section 4
        # ----------------------------------------------------

        elif number == "4":

            modules = self._extract_modules(
                text
            )

            section["modules"] = modules

            section["selection"] = {
                "type": "mandatory"
            }

        # ----------------------------------------------------
        # Section 5
        # ----------------------------------------------------

        elif number == "5":

            modules = self._extract_modules(
                text
            )

            # Team Challenge is mandatory.
            mandatory_modules = [
                module
                for module in modules
                if module["module_code"]
                == "255030-009"
            ]

            selection_modules = [
                module
                for module in modules
                if module["module_code"]
                in {
                    "255030-010",
                    "255030-011",
                }
            ]

            section["modules"] = mandatory_modules

            section["selection_groups"] = [
                {
                    "selection_type": "exactly_one",
                    "modules": selection_modules,
                }
            ]

        # ----------------------------------------------------
        # Section 6
        # ----------------------------------------------------

        elif number == "6":

            modules = self._extract_modules(
                text
            )

            section["modules"] = modules

            section["selection"] = {
                "type": "mandatory"
            }

        return section

    # ========================================================
    # NORMALIZE EXISTING SECTION
    # ========================================================

    def _normalize_section(self, section):

        section = dict(section)

        section["text"] = self._normalize_text(
            section.get("text", "")
        )

        if "modules" in section:

            section["modules"] = [
                self._normalize_module(module)
                for module in section["modules"]
            ]

        if "selection_groups" in section:

            section["selection_groups"] = (
                self._normalize_selection_groups(
                    section["selection_groups"]
                )
            )

        if "conditional_modules" in section:

            section["conditional_modules"] = (
                self._normalize_conditional_modules(
                    section["conditional_modules"]
                )
            )

        return section

    # ========================================================
    # EXTRACT MODULES
    # ========================================================

    def _extract_modules(self, text):

        modules = []

        for match in self.MODULE_CODE_PATTERN.finditer(
            text
        ):

            module = {
                "module_code": match.group("code"),
                "module_name": self._normalize_text(
                    match.group("name")
                ),
                "credits": int(
                    match.group("credits")
                ),
                "requirement": self._normalize_text(
                    match.group("requirement")
                ),
            }

            modules.append(module)

        return modules

    # ========================================================
    # SELECTION CREDITS
    # ========================================================

    def _extract_selection_credits(self, text):

        match = re.search(
            r"Gesamtumfang von\s+(\d+)\s+LP",
            text,
            flags=re.IGNORECASE,
        )

        if match:

            return int(match.group(1))

        return None

    # ========================================================
    # CONDITIONAL MODULES
    # ========================================================

    def _extract_conditional_modules(self, text):

        conditional_modules = []

        # ----------------------------------------------------
        # A1
        # ----------------------------------------------------

        a1_match = re.search(
            r"Studenten,\s+deren Muttersprache nicht Deutsch ist"
            r".*?"
            r"Sprachniveau A1.*?"
            r"Modul\s+"
            r"(?P<code>136004-005)\s+"
            r"(?P<name>Deutsch als Fremdsprache I "
            r"\(Niveau A1\))",
            text,
            flags=re.IGNORECASE,
        )

        if a1_match:

            condition = (
                "Studenten, deren Muttersprache nicht "
                "Deutsch ist und die für die deutsche "
                "Sprache das Sprachniveau A1 des "
                "Gemeinsamen Europäischen "
                "Referenzrahmens für Sprachen nicht "
                "nachweisen,"
            )

            conditional_modules.append(
                {
                    "condition": self._normalize_text(
                        condition
                    ),
                    "module": {
                        "module_code": "136004-005",
                        "module_name": (
                            "Deutsch als Fremdsprache I "
                            "(Niveau A1)"
                        ),
                        "credits": 5,
                        "requirement": "Wahlpflichtmodul",
                    },
                }
            )

        # ----------------------------------------------------
        # A2
        # ----------------------------------------------------

        a2_match = re.search(
            r"Studenten,\s+deren Muttersprache nicht Deutsch ist"
            r".*?"
            r"Sprachniveau A2.*?"
            r"Modul\s+"
            r"(?P<code>136004-006)\s+"
            r"(?P<name>Deutsch als Fremdsprache II "
            r"\(Niveau A2\))",
            text,
            flags=re.IGNORECASE,
        )

        if a2_match:

            condition = (
                "Studenten, deren Muttersprache nicht "
                "Deutsch ist und die für die deutsche "
                "Sprache das Sprachniveau A2 des "
                "Gemeinsamen Europäischen "
                "Referenzrahmens für Sprachen nicht "
                "nachweisen,"
            )

            conditional_modules.append(
                {
                    "condition": self._normalize_text(
                        condition
                    ),
                    "module": {
                        "module_code": "136004-006",
                        "module_name": (
                            "Deutsch als Fremdsprache II "
                            "(Niveau A2)"
                        ),
                        "credits": 5,
                        "requirement": "Wahlpflichtmodul",
                    },
                }
            )

        return conditional_modules

    # ========================================================
    # STUDY PROGRESSION
    # ========================================================

    def _extract_study_progression(self, text):

        match = re.search(
            r"(?P<paragraph>\(2\))\s+"
            r"(?P<text>Der empfohlene Ablauf.*)",
            text,
            flags=re.IGNORECASE,
        )

        if not match:

            return None

        return {
            "paragraph": match.group("paragraph"),
            "text": self._normalize_text(
                match.group("text")
            ),
        }

    # ========================================================
    # MODULE NORMALIZATION
    # ========================================================

    def _normalize_module(self, module):

        module = dict(module)

        if "module_name" in module:

            module["module_name"] = (
                self._normalize_text(
                    module["module_name"]
                )
            )

        if "module_code" in module:

            module["module_code"] = (
                module["module_code"].strip()
            )

        if "credits" in module:

            try:

                module["credits"] = int(
                    module["credits"]
                )

            except (
                ValueError,
                TypeError,
            ):

                pass

        if "requirement" in module:

            module["requirement"] = (
                self._normalize_text(
                    module["requirement"]
                )
            )

        return module

    # ========================================================
    # SELECTION GROUPS
    # ========================================================

    def _normalize_selection_groups(
        self,
        groups,
    ):

        normalized_groups = []

        for group in groups:

            group = dict(group)

            if "modules" in group:

                group["modules"] = [
                    self._normalize_module(module)
                    for module in group["modules"]
                ]

            normalized_groups.append(group)

        return normalized_groups

    # ========================================================
    # CONDITIONAL MODULE NORMALIZATION
    # ========================================================

    def _normalize_conditional_modules(
        self,
        conditional_modules,
    ):

        normalized = []

        for conditional in conditional_modules:

            condition = self._normalize_text(
                conditional.get(
                    "condition",
                    "",
                )
            )

            module = conditional.get(
                "module",
                {},
            )

            module = self._normalize_module(
                module
            )

            module["module_name"] = (
                self._clean_conditional_module_name(
                    module.get(
                        "module_name",
                        "",
                    )
                )
            )

            normalized.append(
                {
                    "condition": condition,
                    "module": module,
                }
            )

        return normalized

    # ========================================================
    # CONDITIONAL MODULE NAME CLEANUP
    # ========================================================

    def _clean_conditional_module_name(
        self,
        name,
    ):

        name = self._normalize_text(
            name
        )

        name = re.sub(
            r"^verpflichtend\s+zu\s+belegen:\s*",
            "",
            name,
            flags=re.IGNORECASE,
        )

        name = re.sub(
            r"^\d{6}-\d{3}\s+",
            "",
            name,
        )

        return name.strip()