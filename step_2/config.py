from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    api_key: str = ""
    model: str = "gemini-2.5-flash"
    docs_dir: Path = ROOT_DIR / "docs"
    cache_dir: Path = ROOT_DIR / "cache"
    cache_file: Path = ROOT_DIR / "cache" / "uploaded_files.json"
    article_url_key: str = "Article URL:"
    chunk_size: int = 800
    chunk_overlap: int = 100
    assistant_name: str = "OptiBot"
    system_prompt: str = (
        "You are OptiBot, the customer-support bot for OptiSigns.com.\n\n"
        "• Tone: helpful, factual, concise.\n"
        "• Only answer using the uploaded docs.\n"
        "• Max 5 bullet points; else link to the doc.\n"
        "• Cite up to 3 \"Article URL:\" lines per reply."
    )


def _parse_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _env_first(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def load_settings() -> Settings:
    _parse_env_file(ROOT_DIR / ".env")

    api_key = _env_first("GEMINI_API_KEY", "GOOGLE_API_KEY", "API_KEY")
    model = os.getenv("MODEL", "gemini-2.5-flash")

    return Settings(
        api_key=api_key,
        model=model,
    )
