from __future__ import annotations

import re
from pathlib import Path

from step_2.config import Settings


def _rank_documents(files: list[Path], question: str, limit: int = 3) -> list[Path]:
    terms = {match.lower() for match in re.findall(r"[A-Za-z0-9]+", question) if len(match) > 2}
    scored: list[tuple[int, Path]] = []

    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        score = sum(1 for term in terms if term in text or term in path.name.lower())
        scored.append((score, path))

    scored.sort(key=lambda item: (item[0], item[1].name), reverse=True)

    selected = [path for score, path in scored if score > 0][:limit]
    return selected or files[:limit]


def test_gemini_assistant(settings: Settings, files: list[Path], question: str) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover - runtime dependency issue
        raise RuntimeError("Please install the google-genai package before testing Gemini.") from exc

    relevant_files = _rank_documents(files, question)

    context_blocks: list[str] = []
    for path in relevant_files:
        context_blocks.append(path.read_text(encoding="utf-8"))

    candidate_models = [settings.model, "gemini-2.5-flash", "gemini-2.0-flash"]
    seen: set[str] = set()
    last_error: Exception | None = None

    client = genai.Client(api_key=settings.api_key)

    for model_name in candidate_models:
        if not model_name or model_name in seen:
            continue
        seen.add(model_name)
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    settings.system_prompt,
                    "\n\n".join(context_blocks),
                    question,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )
        except Exception as exc:  # pragma: no cover - runtime API/model issue
            last_error = exc
            continue
        return (response.text or "").strip()

    if last_error is not None:
        raise last_error
    return ""
