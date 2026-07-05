from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests
from markdownify import markdownify as md

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
METADATA_DIR = ROOT / "metadata"
API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"

DOCS_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)

INTERNAL_ARTICLE_URL_PATTERN = re.compile(
    r"https://support\.optisigns\.com/hc/en-us/articles/(\d+)(?:-[^)\s?#]+)?"
)
MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")


def slugify(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^a-z0-9]+", "-", title)
    title = re.sub(r"-+", "-", title).strip("-")
    return title or "article"


def clean_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = INTERNAL_ARTICLE_URL_PATTERN.sub(r"/hc/en-us/articles/\1", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = MULTIPLE_BLANK_LINES.sub("\n\n", text)
    return text.strip()


def fetch_articles(page: int = 1, per_page: int = 100) -> dict[str, Any]:
    response = requests.get(
        API_URL,
        params={"page": page, "per_page": per_page},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def write_article_markdown(article: dict[str, Any], slug_counts: dict[str, int]) -> str:
    article_id = str(article.get("id"))
    title = article.get("title") or article.get("name") or f"article-{article_id}"
    updated_at = article.get("updated_at") or article.get("edited_at") or ""
    html_url = article.get("html_url") or ""
    body = article.get("body") or ""

    slug = slugify(title)
    slug_counts[slug] = slug_counts.get(slug, 0) + 1
    if slug_counts[slug] > 1:
        slug = f"{slug}-{slug_counts[slug]}"

    markdown_body = clean_markdown(md(body, heading_style="ATX"))
    output = (
        f"Article URL:\n{html_url}\n\n"
        f"Updated At:\n{updated_at}\n\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{markdown_body}\n"
    )

    output_path = DOCS_DIR / f"{slug}.md"
    output_path.write_text(output, encoding="utf-8")
    return str(output_path.relative_to(ROOT))


def main() -> None:
    first_page = fetch_articles(page=1, per_page=50)
    articles = first_page.get("articles", [])[:50]

    slug_counts: dict[str, int] = {}
    metadata: dict[str, dict[str, str]] = {}

    for article in articles:
        article_id = str(article.get("id"))
        relative_path = write_article_markdown(article, slug_counts)
        metadata[article_id] = {
            "title": article.get("title") or article.get("name") or f"article-{article_id}",
            "updated_at": article.get("updated_at") or article.get("edited_at") or "",
            "file": relative_path,
            "html_url": article.get("html_url") or "",
        }

    metadata_path = METADATA_DIR / "articles.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(articles)} markdown files to {DOCS_DIR}")
    print(f"Wrote metadata to {metadata_path}")


if __name__ == "__main__":
    main()
