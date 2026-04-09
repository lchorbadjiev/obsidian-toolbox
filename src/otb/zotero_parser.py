"""Parser for Zotero annotation exports (HTML and markdown)."""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from otb.epub_figures import FigureMap
from otb.parser import Annotation, Book, FigureRef, _title_from_text
from otb.pdf_figures import (
    detect_zotero_figure_refs,
    extract_pdf_figures,
    merge_split_annotations,
)
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


_PAGE_RE = re.compile(r"p\.\s*(\w+)")
_COLOR_RE = re.compile(r"background-color:\s*#([a-fA-F0-9]{6,8})")


def _parse_html_annotations(  # pylint: disable=too-many-locals  # HTML element traversal requires tracking multiple attributes
    html_path: Path,
) -> list[tuple[str, str, str | None]]:
    """Parse Zotero HTML export and return (text, page, color) tuples.

    Color is a 6-digit hex string (e.g., '#ffd400') or None.
    """
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    entries: list[tuple[str, str, str | None]] = []

    for p_tag in soup.find_all("p"):
        highlight = p_tag.find("span", class_="highlight")
        citation = p_tag.find("span", class_="citation-item")
        if not highlight or not citation:
            continue

        # Extract text (strip surrounding quotes)
        ann_text = highlight.get_text().strip()
        if ann_text.startswith("\u201c") and ann_text.endswith("\u201d"):
            ann_text = ann_text[1:-1]
        elif ann_text.startswith('"') and ann_text.endswith('"'):
            ann_text = ann_text[1:-1]

        # Extract page
        citation_text = citation.get_text()
        page_match = _PAGE_RE.search(citation_text)
        page = page_match.group(1) if page_match else ""

        # Extract color from background-color style
        color: str | None = None
        colored_span = highlight.find("span", style=True)
        if colored_span:
            style = str(colored_span.get("style", ""))
            color_match = _COLOR_RE.search(style)
            if color_match:
                hex_val = color_match.group(1)
                # Strip alpha channel (last 2 digits if 8-digit hex)
                color = f"#{hex_val[:6]}"

        entries.append((ann_text, page, color))

    return entries


def _find_pdf(directory: Path) -> Path | None:
    """Find a single .pdf file in directory, or None."""
    candidates = list(directory.glob("*.pdf"))
    return candidates[0] if len(candidates) == 1 else None


def parse_zotero_annotations(  # pylint: disable=too-many-locals,too-many-branches  # format detection + extract-fix-build pipeline
    directory: Path, verbose: bool = False,
) -> tuple[list[Annotation], FigureMap]:
    """Parse Zotero annotation exports from a directory.

    The directory must contain book.txt and either
    Annotations.html (preferred) or Annotations.md.
    Optionally extracts figures from a PDF if present.
    Returns a tuple of (annotations, figure_map).

    Raises FileNotFoundError if book.txt or annotation file missing.
    Raises RuntimeError if aspell is not installed.
    """
    check_aspell_available()
    book = parse_book_metadata(directory / "book.txt")

    # Detect format: prefer HTML over markdown
    html_path = directory / "Annotations.html"
    md_path = directory / "Annotations.md"

    if html_path.exists():
        raw_with_color = _parse_html_annotations(html_path)
        raw_texts = [text for text, _, _ in raw_with_color]
        raw_pages = [page for _, page, _ in raw_with_color]
        raw_colors: list[str | None] = [
            color for _, _, color in raw_with_color
        ]
    elif md_path.exists():
        raw_entries: list[tuple[str, str]] = []
        for line in md_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if (not stripped or stripped.startswith("#")
                    or stripped.startswith("(")):
                continue
            match = _ANNOTATION_RE.search(stripped)
            if match:
                raw_entries.append((match.group(1), match.group(2)))
            else:
                print(
                    f"Warning: skipping unparseable line: "
                    f"{stripped[:60]}...",
                    file=sys.stderr,
                )
        raw_texts = [t for t, _ in raw_entries]
        raw_pages = [p for _, p in raw_entries]
        raw_colors = [None] * len(raw_entries)
    else:
        raise FileNotFoundError(
            f"No Annotations.html or Annotations.md in {directory}"
        )

    # Fix concatenated words across all texts
    fixed_texts, fix_count = fix_concatenated_words(
        raw_texts, verbose=verbose,
    )
    if fix_count:
        print(
            f"Fixed {fix_count} concatenated words.",
            file=sys.stderr,
        )

    # Build Annotation objects
    annotations: list[Annotation] = []
    for page, fixed_text, color in zip(
        raw_pages, fixed_texts, raw_colors,
    ):
        annotations.append(
            Annotation(
                book=book,
                chapter="",
                page=page,
                location=0,
                text=fixed_text,
                title=_title_from_text(fixed_text),
                color=color,
            )
        )

    # Merge split annotations if PDF available
    pdf_path = _find_pdf(directory)
    annotations = merge_split_annotations(annotations, pdf_path)

    for i, a in enumerate(annotations, start=1):
        a.number = i

    # Extract figures from PDF if present
    figure_map: FigureMap = {}
    if pdf_path:
        all_refs: list[tuple[str, str]] = []
        for a in annotations:
            refs = detect_zotero_figure_refs(a.text, a.page)
            for label, page_str in refs:
                a.figures.append(FigureRef(label=label))
                all_refs.append((label, page_str))
        if all_refs:
            figure_map = extract_pdf_figures(pdf_path, all_refs)

    return annotations, figure_map
