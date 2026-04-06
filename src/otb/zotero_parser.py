"""Parser for Zotero annotation markdown exports."""
import re
import sys
from pathlib import Path

from otb.parser import Annotation, Book, _title_from_text

_ROMAN_MAP = {
    "m": 1000, "cm": 900, "d": 500, "cd": 400,
    "c": 100, "xc": 90, "l": 50, "xl": 40,
    "x": 10, "ix": 9, "v": 5, "iv": 4, "i": 1,
}
_ROMAN_RE = re.compile(r"^[mdclxvi]+$", re.IGNORECASE)


def _roman_to_int(s: str) -> int:
    """Convert a Roman numeral string to an integer."""
    result = 0
    s_lower = s.lower()
    idx = 0
    for roman, value in _ROMAN_MAP.items():
        while s_lower[idx:].startswith(roman):
            result += value
            idx += len(roman)
    return result


def _parse_page(raw: str) -> int:
    """Parse a page string as int, handling Roman numerals."""
    if raw.isdigit():
        return int(raw)
    if _ROMAN_RE.match(raw):
        return _roman_to_int(raw)
    return int(raw)


def parse_book_metadata(path: Path) -> Book:
    """Parse a Zotero book.txt metadata file and return a Book.

    Raises FileNotFoundError if the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    fields: dict[str, str] = {}
    i = 0
    while i < len(lines) - 1:
        label = lines[i].strip()
        value = lines[i + 1].strip()
        if label:
            fields[label] = value
        i += 2
    title = fields.get("Title", "")
    author = fields.get("Authors", "")
    return Book(title=title, author=author)


# Smart quotes used in Zotero exports: \u201c = left ", \u201d = right "
_ANNOTATION_RE = re.compile(
    r"\u201c(.+?)\u201d\s+\(\u201c.*?\u201d,\s*p\.\s*(\w+)\)"
)


def parse_zotero_annotations(directory: Path) -> list[Annotation]:
    """Parse Zotero annotation exports from a directory.

    The directory must contain book.txt and Annotations.md.
    Returns a list of Annotation objects with sequential numbering.

    Raises FileNotFoundError if book.txt or Annotations.md is missing.
    """
    book = parse_book_metadata(directory / "book.txt")
    ann_path = directory / "Annotations.md"
    if not ann_path.exists():
        raise FileNotFoundError(f"File not found: {ann_path}")
    text = ann_path.read_text(encoding="utf-8")

    annotations: list[Annotation] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("("):
            continue
        match = _ANNOTATION_RE.search(stripped)
        if match:
            ann_text = match.group(1)
            page_raw = match.group(2)
            try:
                page = _parse_page(page_raw)
            except ValueError:
                print(
                    f"Warning: skipping annotation with unparseable page "
                    f"'{page_raw}': {ann_text[:40]}...",
                    file=sys.stderr,
                )
                continue
            annotations.append(
                Annotation(
                    book=book,
                    chapter="",
                    page=page,
                    location=page,
                    text=ann_text,
                    title=_title_from_text(ann_text),
                    color=None,
                )
            )
        else:
            print(
                f"Warning: skipping unparseable line: {stripped[:60]}...",
                file=sys.stderr,
            )

    for i, a in enumerate(annotations, start=1):
        a.number = i

    return annotations
