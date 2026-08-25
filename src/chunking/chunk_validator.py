import json
from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# Expected regulation structure
# ============================================================

EXPECTED_REGULATION_PARAGRAPHS = {
    "§ 1",
    "§ 2",
    "§ 3",
    "§ 4",
    "§ 5",
    "§ 7",
    "§ 8",
    "§ 9",
    "§ 10",
    "§ 11",
}


EXPECTED_SECTION_NUMBERS = {
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
}


# ============================================================
# Expected module structure
# ============================================================

EXPECTED_MODULE_COUNT = 38


# These modules are conditional modules mentioned in §6,
# section 3. They are valid module descriptions but may not
# have a direct curriculum mapping in the curriculum index.
CONDITIONAL_MODULES = {
    "136004-005",
    "136004-006",
}


# ============================================================
# Required chunk fields
# ============================================================

REQUIRED_FIELDS = {
    "chunk_id",
    "chunk_index",
    "document_id",
    "chunk_type",
    "text",
    "context",
    "zone",
}


# ============================================================
# Validation exception
# ============================================================

class ChunkValidationError(Exception):
    """
    Raised when persisted chunks fail validation.
    """

    pass


# ============================================================
# Validator
# ============================================================

class ChunkValidator:
    """
    Validate the canonical persisted chunks.jsonl.

    The validator checks:

    - JSON validity
    - total chunk count
    - required fields
    - unique chunk IDs
    - continuous chunk indices
    - non-empty text
    - regulation paragraphs
    - §6 section chunks
    - module chunk count
    - module uniqueness
    - curriculum metadata
    - known conditional module exceptions
    """

    def __init__(self, path: str):

        self.path = Path(path)

    # ========================================================
    # Load persisted chunks
    # ========================================================

    def load(self) -> List[Dict[str, Any]]:

        if not self.path.exists():

            raise ChunkValidationError(
                f"Chunk file does not exist: {self.path}"
            )

        chunks: List[Dict[str, Any]] = []

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1,
            ):

                line = line.strip()

                # Ignore completely empty lines
                if not line:
                    continue

                try:

                    chunk = json.loads(line)

                except json.JSONDecodeError as exc:

                    raise ChunkValidationError(
                        f"Invalid JSON at line "
                        f"{line_number}: {exc}"
                    ) from exc

                if not isinstance(
                    chunk,
                    dict,
                ):

                    raise ChunkValidationError(
                        f"Line {line_number} "
                        f"is not a JSON object."
                    )

                chunks.append(chunk)

        return chunks

    # ========================================================
    # Main validation entry point
    # ========================================================

    def validate(self) -> None:

        chunks = self.load()

        print("\n" + "=" * 80)
        print("CHUNK VALIDATION")
        print("=" * 80)

        print(
            f"Loaded chunks: {len(chunks)}"
        )

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        self._validate_total_count(
            chunks
        )

        self._validate_required_fields(
            chunks
        )

        self._validate_chunk_ids(
            chunks
        )

        self._validate_chunk_indices(
            chunks
        )

        self._validate_text(
            chunks
        )

        # ----------------------------------------------------
        # Regulation validation
        # ----------------------------------------------------

        self._validate_regulations(
            chunks
        )

        self._validate_section_chunks(
            chunks
        )

        # ----------------------------------------------------
        # Module validation
        # ----------------------------------------------------

        self._validate_modules(
            chunks
        )

        print("\n" + "=" * 80)
        print("VALIDATION PASSED")
        print("=" * 80)

    # ========================================================
    # Total count
    # ========================================================

    def _validate_total_count(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        expected = 54
        actual = len(chunks)

        if actual != expected:

            raise ChunkValidationError(
                f"Expected {expected} chunks, "
                f"found {actual}."
            )

        print(
            f"[OK] Total chunks: {actual}"
        )

    # ========================================================
    # Required fields
    # ========================================================

    def _validate_required_fields(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        for chunk in chunks:

            missing = (
                REQUIRED_FIELDS
                - chunk.keys()
            )

            if missing:

                raise ChunkValidationError(
                    f"Chunk "
                    f"'{chunk.get('chunk_id')}' "
                    f"is missing fields: "
                    f"{sorted(missing)}"
                )

        print(
            "[OK] Required fields present"
        )

    # ========================================================
    # Chunk IDs
    # ========================================================

    def _validate_chunk_ids(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        ids = [
            chunk["chunk_id"]
            for chunk in chunks
        ]

        seen = set()
        duplicates = set()

        for chunk_id in ids:

            if chunk_id in seen:

                duplicates.add(
                    chunk_id
                )

            seen.add(
                chunk_id
            )

        if duplicates:

            raise ChunkValidationError(
                "Duplicate chunk IDs: "
                f"{sorted(duplicates)}"
            )

        print(
            "[OK] Chunk IDs are unique"
        )

    # ========================================================
    # Chunk indices
    # ========================================================

    def _validate_chunk_indices(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        indices = [
            chunk["chunk_index"]
            for chunk in chunks
        ]

        expected = list(
            range(len(chunks))
        )

        if indices != expected:

            raise ChunkValidationError(
                "Chunk indices are not continuous "
                "or not in persisted order.\n"
                f"Expected: {expected}\n"
                f"Actual:   {indices}"
            )

        print(
            "[OK] Chunk indices are continuous"
        )

    # ========================================================
    # Chunk text
    # ========================================================

    def _validate_text(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        for chunk in chunks:

            text = chunk.get(
                "text"
            )

            if not isinstance(
                text,
                str,
            ):

                raise ChunkValidationError(
                    f"Chunk "
                    f"'{chunk['chunk_id']}' "
                    f"has non-string text."
                )

            if not text.strip():

                raise ChunkValidationError(
                    f"Chunk "
                    f"'{chunk['chunk_id']}' "
                    f"has empty text."
                )

        print(
            "[OK] All chunks contain text"
        )

    # ========================================================
    # Regulation validation
    # ========================================================

    def _validate_regulations(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        regulation_chunks = [
            chunk
            for chunk in chunks
            if chunk["chunk_type"]
            in {
                "regulation_paragraph",
                "regulation_section",
            }
        ]

        paragraph_chunks = [
            chunk
            for chunk in regulation_chunks
            if chunk["chunk_type"]
            == "regulation_paragraph"
        ]

        actual_paragraphs = {
            chunk["context"].get(
                "paragraph"
            )
            for chunk in paragraph_chunks
        }

        # ----------------------------------------------------
        # Validate §1-§5 and §7-§11
        # ----------------------------------------------------

        if (
            actual_paragraphs
            != EXPECTED_REGULATION_PARAGRAPHS
        ):

            missing = (
                EXPECTED_REGULATION_PARAGRAPHS
                - actual_paragraphs
            )

            unexpected = (
                actual_paragraphs
                - EXPECTED_REGULATION_PARAGRAPHS
            )

            raise ChunkValidationError(
                "Regulation paragraph mismatch.\n"
                f"Missing: {sorted(missing)}\n"
                f"Unexpected: {sorted(unexpected)}"
            )

        # ----------------------------------------------------
        # There should be exactly 10 normal paragraphs
        #
        # §6 is represented by 6 section chunks instead
        # of a normal paragraph chunk.
        # ----------------------------------------------------

        if len(paragraph_chunks) != 10:

            raise ChunkValidationError(
                "Expected 10 normal regulation "
                "paragraph chunks, "
                f"found {len(paragraph_chunks)}."
            )

        print(
            "[OK] Regulation paragraphs "
            "§1–§5 and §7–§11 present"
        )

    # ========================================================
    # §6 section validation
    # ========================================================

    def _validate_section_chunks(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        sections = [
            chunk
            for chunk in chunks
            if chunk["chunk_type"]
            == "regulation_section"
        ]

        # ----------------------------------------------------
        # §6 should have six section chunks
        # ----------------------------------------------------

        if len(sections) != 6:

            raise ChunkValidationError(
                "Expected 6 §6 section chunks, "
                f"found {len(sections)}."
            )

        actual_sections = {
            chunk["context"].get(
                "section"
            )
            for chunk in sections
        }

        # ----------------------------------------------------
        # Validate section numbers
        # ----------------------------------------------------

        if (
            actual_sections
            != EXPECTED_SECTION_NUMBERS
        ):

            missing = (
                EXPECTED_SECTION_NUMBERS
                - actual_sections
            )

            unexpected = (
                actual_sections
                - EXPECTED_SECTION_NUMBERS
            )

            raise ChunkValidationError(
                "§6 section mismatch.\n"
                f"Missing: {sorted(missing)}\n"
                f"Unexpected: {sorted(unexpected)}"
            )

        # ----------------------------------------------------
        # Every section must belong to §6
        # ----------------------------------------------------

        for chunk in sections:

            context = chunk["context"]

            if context.get(
                "paragraph"
            ) != "§ 6":

                raise ChunkValidationError(
                    f"Section chunk "
                    f"'{chunk['chunk_id']}' "
                    f"does not belong to §6."
                )

            if not context.get(
                "section_title"
            ):

                raise ChunkValidationError(
                    f"Section chunk "
                    f"'{chunk['chunk_id']}' "
                    f"has no section title."
                )

        print(
            "[OK] §6 sections 1–6 present"
        )

    # ========================================================
    # Module validation
    # ========================================================

    def _validate_modules(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        modules = [
            chunk
            for chunk in chunks
            if chunk["chunk_type"]
            == "module_description"
        ]

        # ----------------------------------------------------
        # Module count
        # ----------------------------------------------------

        if len(modules) != EXPECTED_MODULE_COUNT:

            raise ChunkValidationError(
                f"Expected "
                f"{EXPECTED_MODULE_COUNT} "
                f"module chunks, "
                f"found {len(modules)}."
            )

        module_codes = set()
        conditional_modules_found = set()

        # ====================================================
        # Validate each module
        # ====================================================

        for chunk in modules:

            context = chunk["context"]

            # ------------------------------------------------
            # Module code
            # ------------------------------------------------

            module_code = context.get(
                "module_code"
            )

            if not module_code:

                raise ChunkValidationError(
                    f"Module chunk "
                    f"'{chunk['chunk_id']}' "
                    f"has no module_code."
                )

            # ------------------------------------------------
            # Duplicate module code
            # ------------------------------------------------

            if module_code in module_codes:

                raise ChunkValidationError(
                    f"Duplicate module code: "
                    f"{module_code}"
                )

            module_codes.add(
                module_code
            )

            # ------------------------------------------------
            # Module name
            # ------------------------------------------------

            if not context.get(
                "module_name"
            ):

                raise ChunkValidationError(
                    f"Module "
                    f"'{module_code}' "
                    f"has no module_name."
                )

            # ------------------------------------------------
            # Curriculum metadata
            # ------------------------------------------------

            curriculum = context.get(
                "curriculum"
            )

            # ------------------------------------------------
            # Conditional module exception
            # ------------------------------------------------

            if not isinstance(
                curriculum,
                dict,
            ):

                if module_code in CONDITIONAL_MODULES:

                    conditional_modules_found.add(
                        module_code
                    )

                    continue

                raise ChunkValidationError(
                    f"Module "
                    f"'{module_code}' "
                    f"has no curriculum context."
                )

            # ------------------------------------------------
            # Validate curriculum metadata
            # ------------------------------------------------

            required_curriculum_fields = {
                "part",
                "paragraph",
                "paragraph_title",
                "section",
                "section_title",
                "module_code",
                "module_name",
                "credits",
                "requirement",
            }

            missing = (
                required_curriculum_fields
                - curriculum.keys()
            )

            if missing:

                raise ChunkValidationError(
                    f"Module "
                    f"'{module_code}' "
                    f"is missing curriculum "
                    f"fields: "
                    f"{sorted(missing)}"
                )

            # ------------------------------------------------
            # Curriculum must point to §6
            # ------------------------------------------------

            if curriculum.get(
                "paragraph"
            ) != "§ 6":

                raise ChunkValidationError(
                    f"Module "
                    f"'{module_code}' "
                    f"is not linked to §6."
                )

            # ------------------------------------------------
            # Curriculum module code must match
            # ------------------------------------------------

            if curriculum.get(
                "module_code"
            ) != module_code:

                raise ChunkValidationError(
                    f"Module code mismatch "
                    f"for '{module_code}'. "
                    f"Curriculum contains: "
                    f"{curriculum.get('module_code')}"
                )

            # ------------------------------------------------
            # Curriculum module name must exist
            # ------------------------------------------------

            if not curriculum.get(
                "module_name"
            ):

                raise ChunkValidationError(
                    f"Module "
                    f"'{module_code}' "
                    f"has no curriculum "
                    f"module_name."
                )

        # ====================================================
        # Validate conditional modules
        # ====================================================

        missing_conditional = (
            CONDITIONAL_MODULES
            - conditional_modules_found
        )

        if missing_conditional:

            # If one of the known conditional modules
            # actually has curriculum metadata, that's fine.
            for code in (
                CONDITIONAL_MODULES
                & module_codes
            ):

                if code not in conditional_modules_found:
                    continue

            # Only fail if the module is completely absent.
            absent = (
                CONDITIONAL_MODULES
                - module_codes
            )

            if absent:

                raise ChunkValidationError(
                    "Expected conditional module(s) "
                    "are missing: "
                    f"{sorted(absent)}"
                )

        # ----------------------------------------------------
        # Information about conditional modules
        # ----------------------------------------------------

        if conditional_modules_found:

            print(
                "[INFO] Conditional modules without "
                "curriculum mapping:"
            )

            for code in sorted(
                conditional_modules_found
            ):

                print(
                    f"       {code}"
                )

        # ----------------------------------------------------
        # Count modules with curriculum mapping
        # ----------------------------------------------------

        mapped_modules = sum(
            1
            for chunk in modules
            if isinstance(
                chunk["context"].get(
                    "curriculum"
                ),
                dict,
            )
        )

        print(
            f"[OK] Module chunks: "
            f"{len(modules)}"
        )

        print(
            f"[OK] Curriculum-linked modules: "
            f"{mapped_modules}"
        )

    # ========================================================
    # Summary
    # ========================================================

    def summary(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:

        regulation_count = sum(
            1
            for chunk in chunks
            if chunk["chunk_type"]
            in {
                "regulation_paragraph",
                "regulation_section",
            }
        )

        regulation_paragraph_count = sum(
            1
            for chunk in chunks
            if chunk["chunk_type"]
            == "regulation_paragraph"
        )

        regulation_section_count = sum(
            1
            for chunk in chunks
            if chunk["chunk_type"]
            == "regulation_section"
        )

        module_count = sum(
            1
            for chunk in chunks
            if chunk["chunk_type"]
            == "module_description"
        )

        print("\nChunk summary:")

        print(
            f"  Regulation chunks       : "
            f"{regulation_count}"
        )

        print(
            f"    Regulation paragraphs : "
            f"{regulation_paragraph_count}"
        )

        print(
            f"    §6 sections           : "
            f"{regulation_section_count}"
        )

        print(
            f"  Module chunks           : "
            f"{module_count}"
        )

        print(
            f"  Total                   : "
            f"{len(chunks)}"
        )