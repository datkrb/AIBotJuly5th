from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from config import Settings


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def load_cache(cache_file: Path) -> dict[str, dict[str, str]]:
    if not cache_file.exists():
        return {}
    return json.loads(cache_file.read_text(encoding="utf-8"))


def save_cache(cache_file: Path, cache_data: dict[str, dict[str, str]]) -> None:
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_manifest(paths: Iterable[Path]) -> dict[str, dict[str, str]]:
    manifest: dict[str, dict[str, str]] = {}
    for path in paths:
        manifest[path.as_posix()] = {"hash": file_hash(path)}
    return manifest


def diff_manifest(current: dict[str, dict[str, str]], cached: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    added: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []

    for relative_path, payload in current.items():
        cached_hash = cached.get(relative_path, {}).get("hash")
        current_hash = payload.get("hash")
        if not cached_hash:
            added.append(relative_path)
        elif cached_hash != current_hash:
            updated.append(relative_path)
        else:
            skipped.append(relative_path)
            
    return {"added": added, "updated": updated, "skipped": skipped}


@dataclass
class UploadStats:
    uploaded_files: int
    embedded_chunks: int
    uploaded_file_ids: list[str] | None = None
    added_files: int = 0
    updated_files: int = 0
    skipped_files: int = 0


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    blocks = re.split(r'\n{2,}', text)
    
    chunks = []
    current_chunk_words = []
    current_header = ""
    
    for block in blocks:
        header_match = re.search(r'^(#{1,6}\s+.*)', block, flags=re.MULTILINE)
        if header_match:
            current_header = header_match.group(1).strip()
            
        block_words = block.split()
        
        if len(current_chunk_words) + len(block_words) > chunk_size and current_chunk_words:
            chunks.append(" ".join(current_chunk_words))
            
            overlap_words = current_chunk_words[-overlap:] if overlap > 0 else []
            context_prefix = [f"[{current_header}]"] if current_header else []
            
            current_chunk_words = context_prefix + overlap_words + block_words
        else:
            current_chunk_words.extend(block_words)
            
        while len(current_chunk_words) > chunk_size:
            chunks.append(" ".join(current_chunk_words[:chunk_size]))
            overlap_words = current_chunk_words[chunk_size - overlap:]
            context_prefix = [f"[{current_header}]"] if current_header else []
            current_chunk_words = context_prefix + overlap_words
            
    if current_chunk_words:
        chunks.append(" ".join(current_chunk_words))
        
    return chunks


def collect_markdown_files(docs_dir: Path) -> list[Path]:
    return sorted(docs_dir.glob("*.md"))


def count_chunks(files: Iterable[Path], chunk_size: int, overlap: int) -> int:
    total = 0
    for path in files:
        total += len(chunk_text(path.read_text(encoding="utf-8"), chunk_size, overlap))
    return total


def upload_to_gemini(settings: Settings, files: list[Path], manifest: dict[str, dict[str, str]]) -> UploadStats:
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - runtime dependency issue
        raise RuntimeError("Please install the google-genai package before uploading with Gemini.") from exc

    client = genai.Client(api_key=settings.api_key)
    uploaded_file_ids: list[str] = []

    for path in files:
        uploaded_file = client.files.upload(file=str(path))
        uploaded_file_ids.append(getattr(uploaded_file, "name", path.name))
        
        # Save URI to manifest
        manifest[path.as_posix()]["uri"] = getattr(uploaded_file, "uri", "")

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
    diff = diff_manifest(manifest, cached)

    # Preserve URIs for skipped files
    for path in diff["skipped"]:
        manifest[path]["uri"] = cached.get(path, {}).get("uri", "")

    changed_paths = diff["added"] + diff["updated"]
    changed_files = [Path(path) for path in changed_paths]
    
    if not changed_files:
        save_cache(settings.cache_file, manifest)
        return UploadStats(
            uploaded_files=0, 
            embedded_chunks=0,
            added_files=len(diff["added"]),
            updated_files=len(diff["updated"]),
            skipped_files=len(diff["skipped"]),
        )

    stats = upload_to_gemini(settings, changed_files, manifest)
    stats.added_files = len(diff["added"])
    stats.updated_files = len(diff["updated"])
    stats.skipped_files = len(diff["skipped"])

    save_cache(settings.cache_file, manifest)
    return stats


if __name__ == "__main__":
    from config import load_settings

    print("Starting manual upload...")
    settings = load_settings()
    stats = upload_delta(settings)
    
    print("\n--- Upload Delta Stats ---")
    print(f"Added Files    : {stats.added_files}")
    print(f"Updated Files  : {stats.updated_files}")
    print(f"Skipped Files  : {stats.skipped_files}")
    print(f"Embedded Chunks: {stats.embedded_chunks}")
    if stats.uploaded_file_ids:
        print(f"Uploaded File IDs : {len(stats.uploaded_file_ids)}")
    print("--------------------------\n")
