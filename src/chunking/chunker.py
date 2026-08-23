import json
from pathlib import Path

from src.models.chunk import Chunk


DOCUMENT_ID = "web_engineering_2025"


class RegulationChunker:

    def __init__(self, regulation_path: Path):
        self.regulation_path = regulation_path

    def load(self) -> dict:
        with open(
            self.regulation_path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    def chunk(self) -> list[Chunk]:

        regulation = self.load()

        chunks: list[Chunk] = []

        for part in regulation.get("parts", []):

            part_name = part.get("part")
            part_title = part.get("title")

            for regulation_section in part.get("regulations", []):

                paragraph = regulation_section.get("paragraph")
                paragraph_title = regulation_section.get("title")

                chunks.extend(
                    self._chunk_paragraph(
                        regulation_section,
                        part_name,
                        part_title,
                        paragraph,
                        paragraph_title
                    )
                )

                chunks.extend(
                    self._chunk_module_sections(
                        regulation_section,
                        part_name,
                        part_title,
                        paragraph,
                        paragraph_title
                    )
                )

        return chunks

    def _chunk_paragraph(
        self,
        regulation_section: dict,
        part: str,
        part_title: str,
        paragraph: str,
        paragraph_title: str
    ) -> list[Chunk]:

        blocks = regulation_section.get("blocks", [])

        if not blocks:
            return []

        text_parts = []

        for block in blocks:

            text = block.get("text")

            if text:
                text_parts.append(text.strip())

        text = "\n\n".join(text_parts).strip()

        if not text:
            return []

        source = regulation_section.get("source", {})

        page_start = source.get("start_page")
        page_end = source.get("end_page")

        chunk_id = (
            f"paragraph_"
            f"{paragraph.replace('§', '').strip().replace(' ', '_')}"
        )

        return [
            Chunk(
                chunk_id=chunk_id,
                chunk_type="paragraph",
                text=(
                    f"{paragraph} – {paragraph_title}\n\n"
                    f"{text}"
                ),
                document_id=DOCUMENT_ID,
                part=part,
                part_title=part_title,
                paragraph=paragraph,
                paragraph_title=paragraph_title,
                page_start=page_start,
                page_end=page_end,
                zone=source.get("zone")
            )
        ]

    def _chunk_module_sections(
        self,
        regulation_section: dict,
        part: str,
        part_title: str,
        paragraph: str,
        paragraph_title: str
    ) -> list[Chunk]:

        chunks = []

        module_sections = regulation_section.get(
            "module_sections",
            []
        )

        for module_section in module_sections:

            section_number = module_section.get("number")
            section_title = module_section.get("title")

            blocks = module_section.get("blocks", [])

            text_parts = []

            for block in blocks:

                text = block.get("text")

                if text:
                    text_parts.append(text.strip())

            text = "\n\n".join(text_parts).strip()

            if text:

                chunk_id = (
                    f"module_section_"
                    f"{paragraph.replace('§', '').strip()}_"
                    f"{section_number}"
                )

                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        chunk_type="module_section",
                        text=(
                            f"{paragraph} – {paragraph_title}\n"
                            f"Modulbereich: {section_title}\n\n"
                            f"{text}"
                        ),
                        document_id=DOCUMENT_ID,
                        part=part,
                        part_title=part_title,
                        paragraph=paragraph,
                        paragraph_title=paragraph_title,
                        section=section_title
                    )
                )

            chunks.extend(
                self._chunk_modules(
                    module_section,
                    part,
                    part_title,
                    paragraph,
                    paragraph_title,
                    section_title
                )
            )

        return chunks

    def _chunk_modules(
        self,
        module_section: dict,
        part: str,
        part_title: str,
        paragraph: str,
        paragraph_title: str,
        section_title: str
    ) -> list[Chunk]:

        chunks = []

        modules = module_section.get("modules", [])

        for module in modules:

            module_code = module.get("module_code")
            module_name = module.get("module_name")
            credits = module.get("credits")
            module_type = module.get("type")

            overview = (
                f"Modul: {module_name}\n"
                f"Modulcode: {module_code}\n"
                f"Modulbereich: {section_title}\n"
                f"Leistungspunkte: {credits}\n"
                f"Typ: {module_type}"
            )

            sources = module.get("sources", {})
            main_source = sources.get("main_regulation", {})

            chunks.append(
                Chunk(
                    chunk_id=f"module_{module_code}",
                    chunk_type="module",
                    text=overview,
                    document_id=DOCUMENT_ID,
                    part=part,
                    part_title=part_title,
                    paragraph=paragraph,
                    paragraph_title=paragraph_title,
                    section=section_title,
                    module_code=module_code,
                    module_name=module_name,
                    page_start=main_source.get("start_page"),
                    page_end=main_source.get("end_page"),
                    zone=main_source.get("zone")
                )
            )

            chunks.extend(
                self._chunk_module_description(
                    module,
                    part,
                    part_title,
                    paragraph,
                    paragraph_title,
                    section_title
                )
            )

        return chunks

    def _chunk_module_description(
        self,
        module: dict,
        part: str,
        part_title: str,
        paragraph: str,
        paragraph_title: str,
        section_title: str
    ) -> list[Chunk]:

        chunks = []

        description = module.get("description")

        if not description:
            return chunks

        module_code = module.get("module_code")
        module_name = module.get("module_name")

        sources = module.get("sources", {})
        source = sources.get("module_description", {})

        fields = [
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
            "duration"
        ]

        for field in fields:

            value = description.get(field)

            if value is None:
                continue

            if not isinstance(value, str):
                value = str(value)

            value = value.strip()

            if not value:
                continue

            text = (
                f"Modul: {module_name}\n"
                f"Modulcode: {module_code}\n"
                f"Modulbereich: {section_title}\n\n"
                f"{self._field_title(field)}:\n"
                f"{value}"
            )

            chunk_id = (
                f"module_{module_code}_"
                f"{field}"
            )

            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    chunk_type="module_field",
                    text=text,
                    document_id=DOCUMENT_ID,
                    part=part,
                    part_title=part_title,
                    paragraph=paragraph,
                    paragraph_title=paragraph_title,
                    section=section_title,
                    module_code=module_code,
                    module_name=module_name,
                    field=field,
                    page_start=source.get("start_page"),
                    page_end=source.get("end_page"),
                    zone=source.get("zone")
                )
            )

        return chunks

    @staticmethod
    def _field_title(field: str) -> str:

        titles = {
            "content": "Inhalt",
            "qualification_goals": "Qualifikationsziele",
            "teaching_forms": "Lehrformen",
            "prerequisites": "Voraussetzungen",
            "applicability": "Verwendbarkeit",
            "credit_requirements": "Voraussetzungen für die Vergabe von Leistungspunkten",
            "examination": "Prüfung",
            "credits_and_grades": "Leistungspunkte und Benotung",
            "frequency": "Häufigkeit",
            "workload": "Arbeitsaufwand",
            "duration": "Dauer"
        }

        return titles.get(field, field)

    @staticmethod
    def save_jsonl(
        chunks: list[Chunk],
        output_path: Path
    ) -> None:

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            for chunk in chunks:
                f.write(
                    chunk.to_json() + "\n"
                )