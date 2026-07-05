from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


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


def diff_manifest(current: dict[str, dict[str, str]], cached: dict[str, dict[str, str]]) -> list[str]:
    changed: list[str] = []
    for relative_path, payload in current.items():
        if cached.get(relative_path, {}).get("hash") != payload.get("hash"):
            changed.append(relative_path)
    return changed
