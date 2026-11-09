# Personal Research Assistant CLI

A small local-first research helper. It indexes Markdown, text, and PDF documents in a folder, finds relevant passages for a question, and writes a Markdown report with source citations and excerpts. It does not send your files to an external service and does not require an API key.

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

## Quick start

Put your own research materials in `sources/` (sample notes are included), then run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python research_cli.py ask "What are the main benefits and risks of serverless architectures?"
```

Use `--sources PATH` to choose a different folder and `--output PATH` to choose the report file. PDF parsing uses `pypdf`; supported inputs are `.pdf`, `.md`, and `.txt`.

## What it does

- Splits source documents into passages and ranks them with TF-IDF cosine similarity.
- Produces a report that separates a short synthesis from cited supporting passages.
- Includes source filename, page number for PDFs, and a short excerpt for each citation.
- Shows a warning when the source folder has no material relevant to the question.

The ranking and synthesis are intentionally transparent and extractive. Review cited passages yourself; this starter does not claim that keyword ranking is a substitute for expert review or a generative model. It does not crawl the web.

## Example output

Reports are saved under `reports/` by default. Each answer includes `[S1]`, `[S2]` citations linked to a source list at the end of the Markdown file.
