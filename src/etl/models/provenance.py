from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional
import json
from pathlib import Path


@dataclass
class Provenance:
    document_id: str
    title: str
    university: str
    degree_program: str
    document_type: str
    regulation_version: str

    source_url: str
    local_filename: str

    sha256: str
    size_bytes: int

    downloaded_at: str

    page_count: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


def create_provenance(
    document_id: str,
    title: str,
    university: str,
    degree_program: str,
    document_type: str,
    regulation_version: str,
    source_url: str,
    local_filename: str,
    sha256: str,
    size_bytes: int,
    page_count: Optional[int] = None,
) -> Provenance:

    return Provenance(
        document_id=document_id,
        title=title,
        university=university,
        degree_program=degree_program,
        document_type=document_type,
        regulation_version=regulation_version,
        source_url=source_url,
        local_filename=local_filename,
        sha256=sha256,
        size_bytes=size_bytes,
        downloaded_at=datetime.now(
            timezone.utc
        ).isoformat(),
        page_count=page_count,
    )


def save_provenance(
    provenance: Provenance,
    path: Path,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            provenance.to_dict(),
            file,
            indent=2,
            ensure_ascii=False,
        )