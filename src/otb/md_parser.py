"""Parser for highlight markdown files."""
import re
from pathlib import Path

from otb.parser import Book, Highlight

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


def parse_highlight_md(path: Path) -> Highlight:
    """Parse a highlight markdown file into a Highlight dataclass."""
    text = path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)

    book = Book(title=fm["source"], author=fm["author"])

    h1 = _H1_RE.search(text)

    blockquote = _BLOCKQUOTE_RE.search(text)
    if not blockquote:
        raise ValueError(f"No blockquote found in {path}")

    return Highlight(
        book=book,
        chapter=fm["chapter"],
        page=int(fm["page"]),
        location=int(fm["location"]),
        text=blockquote.group(1),
        title=h1.group(1) if h1 else "",
        number=int(fm["number"]) if "number" in fm else 0,
    )


def parse_highlight_dir(directory: Path) -> list[Highlight]:
    """Parse all highlight markdown files in a directory, sorted by filename."""
    return [parse_highlight_md(p) for p in sorted(directory.glob("*.md"))]
