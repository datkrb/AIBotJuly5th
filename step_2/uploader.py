from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from step_2.config import Settings
from step_2.sync import build_manifest, diff_manifest, load_cache, save_cache


@dataclass
class UploadStats:
    uploaded_files: int
    embedded_chunks: int
    uploaded_file_ids: list[str] | None = None


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size)
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def collect_markdown_files(docs_dir: Path) -> list[Path]:
    return sorted(docs_dir.glob("*.md"))


def count_chunks(files: Iterable[Path], chunk_size: int, overlap: int) -> int:
    total = 0
    for path in files:
        total += len(chunk_text(path.read_text(encoding="utf-8"), chunk_size, overlap))
    return total


def upload_to_gemini(settings: Settings, files: list[Path]) -> UploadStats:
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - runtime dependency issue
        raise RuntimeError("Please install the google-genai package before uploading with Gemini.") from exc

    client = genai.Client(api_key=settings.api_key)
    uploaded_file_ids: list[str] = []

    for path in files:
        uploaded_file = client.files.upload(file=str(path))
        uploaded_file_ids.append(getattr(uploaded_file, "name", path.name))

    chunk_total = count_chunks(files, settings.chunk_size, settings.chunk_overlap)

    return UploadStats(
        uploaded_files=len(files),
        embedded_chunks=chunk_total,
        uploaded_file_ids=uploaded_file_ids,
    )


def upload_delta(settings: Settings) -> UploadStats:
    docs_dir = settings.docs_dir
    files = collect_markdown_files(docs_dir)
    manifest = build_manifest(files)
    cached = load_cache(settings.cache_file)
    changed_paths = diff_manifest(manifest, cached)

    changed_files = [Path(path) for path in changed_paths]
    if not changed_files:
        return UploadStats(uploaded_files=0, embedded_chunks=0)

    stats = upload_to_gemini(settings, changed_files)

    save_cache(settings.cache_file, manifest)
    return stats
