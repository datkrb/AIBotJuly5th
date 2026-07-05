from __future__ import annotations

from config import load_settings
from scraper import main as scrape_articles
from uploader import collect_markdown_files, upload_delta

def main() -> None:
    print("Starting daily job: Re-scraping articles...")
    scrape_articles()

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




if __name__ == "__main__":
    main()
