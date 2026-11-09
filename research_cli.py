import argparse
import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SUPPORTED = {".md", ".txt", ".pdf"}


def read_documents(root: Path):
    documents = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        try:
            if path.suffix.lower() == ".pdf":
                for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
                    text = page.extract_text() or ""
                    if text.strip():
                        documents.append((path, page_number, text))
            else:
                text = path.read_text(encoding="utf-8", errors="replace")
                if text.strip():
                    documents.append((path, None, text))
        except Exception as exc:
            print(f"Skipping {path}: {exc}")
    return documents


def passages(documents, max_words=180):
    chunks = []
    for path, page, text in documents:
        paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text)]
        for paragraph in paragraphs:
            words = paragraph.split()
            for start in range(0, len(words), max_words):
                piece = " ".join(words[start:start + max_words]).strip()
                if len(piece) > 30:
                    chunks.append({"path": path, "page": page, "text": piece})
    return chunks


def research(question, chunks, limit=6):
    if not chunks:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([question] + [item["text"] for item in chunks])
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    ranked = sorted(zip(scores, chunks), key=lambda item: item[0], reverse=True)
    return [(float(score), chunk) for score, chunk in ranked[:limit] if score > 0]


def write_report(question, results, output):
    lines = [f"# Research: {question}", "", f"Generated: {datetime.now().astimezone().isoformat(timespec='minutes')}", "", "## Evidence-based overview", ""]
    if not results:
        lines += ["No relevant passages were found in the selected source folder. Add material or try a more specific question.", ""]
    else:
        lines.append("The passages below are the strongest matches in your local sources. Use them to build your own conclusion; the CLI does not invent a synthesis beyond the retrieved evidence.")
        lines.append("")
        lines.append("## Retrieved passages")
        lines.append("")
        for index, (score, item) in enumerate(results, start=1):
            page = f", p. {item['page']}" if item["page"] else ""
            lines += [f"### [S{index}] {item['path'].name}{page}", "", item["text"], "", f"Relevance score: {score:.3f}", ""]
        lines += ["## Sources", ""]
        for index, (_, item) in enumerate(results, start=1):
            page = f" (page {item['page']})" if item["page"] else ""
            lines.append(f"- [S{index}] `{item['path'].as_posix()}`{page}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Search local research documents and save a cited evidence report.")
    parser.add_argument("question", nargs="+", help="Research question")
    parser.add_argument("--sources", type=Path, default=Path("sources"), help="Folder of PDF, Markdown, and text files")
    parser.add_argument("--output", type=Path, help="Report path (default: reports/<timestamp>.md)")
    parser.add_argument("--limit", type=int, default=6, help="Maximum passages to retrieve")
    args = parser.parse_args()
    question = " ".join(args.question).strip()
    if not question:
        parser.error("question must not be empty")
    if args.limit < 1:
        parser.error("--limit must be at least 1")
    source_dir = args.sources.expanduser().resolve()
    if not source_dir.is_dir():
        parser.error(f"source folder does not exist: {source_dir}")
    chunks = passages(read_documents(source_dir))
    results = research(question, chunks, args.limit)
    output = args.output or Path("reports") / f"research-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    write_report(question, results, output)
    print(f"Indexed {len(chunks)} passages; retrieved {len(results)} relevant passages.")
    print(f"Report saved to {output}")


if __name__ == "__main__":
    main()
