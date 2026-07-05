# OptiSigns Mini-Clone

## Structure by step

```text
.env.sample
Dockerfile
config.py
scraper.py
uploader.py
main.py

docs/
├── *.md

cache/
└── uploaded_files.json
```

## What each file does

- `scraper.py`: Scrape OptiSigns Help Center articles and write them to `docs/*.md`.
- `uploader.py`: Syncs and uploads the Markdown docs to Gemini (using delta logic).
- `main.py`: Re-run the pipeline daily (scrape -> upload delta).

## Chunking strategy

- Chunk size: 800 tokens
- Overlap: 100 tokens

The code currently uses a simple word-based approximation for chunk counting. If you need exact token counts, swap the chunker for a tokenizer from your chosen LLM SDK.

## How to run

```bash
python main.py
```

## Environment variables

- `API_KEY=...`
- `MODEL=gemini-2.5-flash`

## Docker

```bash
docker build -t optisigns-mini-clone .
docker run --rm -e API_KEY=... optisigns-mini-clone
```

## Daily Job Logs

[Link to daily job logs] (Insert your link here)

## Assistant Screenshot

![Assistant answering sample question](Replace_With_Your_Screenshot_Path.png)
