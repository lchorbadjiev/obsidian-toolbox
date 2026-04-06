"""Parser for annotation markdown files."""
import re
from pathlib import Path

from otb.parser import Annotation, Book

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_FRONTMATTER_LINE_RE = re.compile(r'^(\w+):\s*"?([^"\n]+)"?\s*$')
_BLOCKQUOTE_RE = re.compile(r"^>\s+(.+)$", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("No frontmatter found")
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        m = _FRONTMATTER_LINE_RE.match(line)
        if m:
            result[m.group(1)] = m.group(2).strip()
    return result


def parse_annotation_md(path: Path) -> Annotation:
    """Parse an annotation markdown file into an Annotation dataclass."""
    text = path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)

    book = Book(title=fm["source"], author=fm["author"])

    h1 = _H1_RE.search(text)

    blockquote = _BLOCKQUOTE_RE.search(text)
    if not blockquote:
        raise ValueError(f"No blockquote found in {path}")

    return Annotation(
        book=book,
        chapter=fm["chapter"],
        page=int(fm["page"]),
        location=int(fm["location"]),
        text=blockquote.group(1),
        title=h1.group(1) if h1 else "",
        number=int(fm["number"]) if "number" in fm else 0,
        anki_id=int(fm["anki_id"]) if "anki_id" in fm else None,
    )


def parse_annotation_dir(directory: Path) -> list[Annotation]:
    """Parse all annotation markdown files in a directory, sorted by filename."""
    return [parse_annotation_md(p) for p in sorted(directory.glob("*.md"))]


def parse_annotation_dir_with_paths(
    directory: Path,
) -> list[tuple[Path, Annotation]]:
    """Parse all annotation markdown files, returning (path, annotation) pairs."""
    return [
        (p, parse_annotation_md(p)) for p in sorted(directory.glob("*.md"))
    ]
