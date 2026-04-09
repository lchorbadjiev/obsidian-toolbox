"""Parser for Zotero annotation markdown exports."""
import re
import sys
from pathlib import Path

from otb.parser import Annotation, Book, _title_from_text
from otb.word_fixer import check_aspell_available, fix_concatenated_words


def parse_book_metadata(path: Path) -> Book:
    """Parse a book.txt metadata file and return a Book.

    Handles label/value pair format used by both Zotero and Boox
    exports. Leading blank lines are stripped so the function works
    regardless of whether the file starts with content or whitespace.

    Raises FileNotFoundError if the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    fields: dict[str, str] = {}
    i = 0
    while i < len(lines) - 1:
        label = lines[i]
        value = lines[i + 1]
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


def parse_zotero_annotations(  # pylint: disable=too-many-locals  # extract-fix-build pipeline
    directory: Path, verbose: bool = False,
) -> list[Annotation]:
    """Parse Zotero annotation exports from a directory.

    The directory must contain book.txt and Annotations.md.
    Returns a list of Annotation objects with sequential numbering.

    Raises FileNotFoundError if book.txt or Annotations.md is missing.
    Raises RuntimeError if aspell is not installed.
    """
    check_aspell_available()
    book = parse_book_metadata(directory / "book.txt")
    ann_path = directory / "Annotations.md"
    if not ann_path.exists():
        raise FileNotFoundError(f"File not found: {ann_path}")
    text = ann_path.read_text(encoding="utf-8")

    # Phase 1: extract raw annotation texts and page strings
    raw_entries: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("("):
            continue
        match = _ANNOTATION_RE.search(stripped)
        if match:
            ann_text = match.group(1)
            page_raw = match.group(2)
            raw_entries.append((ann_text, page_raw))
        else:
            print(
                f"Warning: skipping unparseable line: {stripped[:60]}...",
                file=sys.stderr,
            )

    # Phase 2: fix concatenated words across all texts
    raw_texts = [t for t, _ in raw_entries]
    fixed_texts, fix_count = fix_concatenated_words(raw_texts, verbose=verbose)
    if fix_count:
        print(
            f"Fixed {fix_count} concatenated words.",
            file=sys.stderr,
        )

    # Phase 3: build Annotation objects from fixed texts
    annotations: list[Annotation] = []
    for (_, page), fixed_text in zip(raw_entries, fixed_texts):
        annotations.append(
            Annotation(
                book=book,
                chapter="",
                page=page,
                location=0,
                text=fixed_text,
                title=_title_from_text(fixed_text),
                color=None,
            )
        )

    for i, a in enumerate(annotations, start=1):
        a.number = i

    return annotations
