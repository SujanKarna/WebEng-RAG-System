from pathlib import Path
from hashlib import sha256
import requests


class DownloadError(Exception):
    """Raised when a document cannot be downloaded."""
    pass


def calculate_sha256(file_path: Path) -> str:
    """
    Calculate the SHA-256 hash of a file.
    """

    digest = sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def download_file(
    url: str,
    destination: Path,
    timeout: int = 30,
) -> dict:
    """
    Download a file and return basic download metadata.
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "TU-Chemnitz-WebEngineering-RAG/1.0"
                )
            },
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise DownloadError(
            f"Failed to download document: {url}"
        ) from exc

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    content = response.content

    # Basic PDF validation.
    if not content.startswith(b"%PDF"):
        raise DownloadError(
            "Downloaded resource does not appear to be a PDF."
        )

    destination.write_bytes(content)

    file_hash = calculate_sha256(destination)

    return {
        "url": url,
        "destination": str(destination),
        "filename": destination.name,
        "size_bytes": len(content),
        "sha256": file_hash,
        "content_type": content_type,
        "status_code": response.status_code,
    }