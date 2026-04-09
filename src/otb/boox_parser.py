"""Parser for Boox e-reader annotation exports."""
import re
from pathlib import Path

from otb.epub_figures import FigureMap, detect_figure_refs, parse_epub_figures
from otb.parser import Annotation, FigureRef, _title_from_text
from otb.zotero_parser import parse_book_metadata


_DATE_PAGE_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+\|\s+Page No\.:\s*(\d+)"
)
_SEPARATOR_RE = re.compile(r"^-{3,}$")


def _find_annotation_file(directory: Path) -> Path:
    """Find the single .txt annotation file (not book.txt) in directory."""
    candidates = [
        f for f in directory.glob("*.txt") if f.name != "book.txt"
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No annotation .txt file found in {directory}"
        )
    if len(candidates) > 1:
        raise FileNotFoundError(
            f"Multiple .txt files found in {directory}, expected one"
        )
    return candidates[0]


def _find_epub(directory: Path) -> Path | None:
    """Find a single .epub file in directory, or None."""
    candidates = list(directory.glob("*.epub"))
    return candidates[0] if len(candidates) == 1 else None


def parse_boox_annotations(  # pylint: disable=too-many-locals,too-many-branches  # line-based state machine with EPUB figure integration
    directory: Path,
) -> tuple[list[Annotation], FigureMap]:
    """Parse Boox annotation exports from a directory.

    The directory must contain book.txt and exactly one other .txt
    annotation file. Optionally extracts figures from an EPUB if
    present. Returns a tuple of (annotations, figure_map).

    Raises FileNotFoundError if book.txt or the annotation file
    is missing.
    """
    book = parse_book_metadata(directory / "book.txt")

    # Load figure map from EPUB if present
    epub_path = _find_epub(directory)
    figure_map: FigureMap = {}
    if epub_path:
        figure_map = parse_epub_figures(epub_path)
    ann_path = _find_annotation_file(directory)
    lines = ann_path.read_text(encoding="utf-8").splitlines()

    annotations: list[Annotation] = []
    current_chapter = ""
    current_location = 0
    text_lines: list[str] = []
    in_annotation = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip header line
        if i == 0 and stripped.startswith("Reading Notes"):
            continue

        # Check for separator
        if _SEPARATOR_RE.match(stripped):
            if in_annotation and text_lines:
                annotations.append(Annotation(
                    book=book,
                    chapter=current_chapter,
                    page="",
                    location=current_location,
                    text=" ".join(text_lines),
                    title=_title_from_text(" ".join(text_lines)),
                    color=None,
                ))
            text_lines = []
            in_annotation = False
            continue

        # Check for date/page line
        match = _DATE_PAGE_RE.match(stripped)
        if match:
            current_location = int(match.group(1))
            in_annotation = True
            text_lines = []
            continue

        # If we're collecting annotation text
        if in_annotation:
            if stripped:
                text_lines.append(stripped)
            continue

        # Otherwise, non-empty line between separators is a chapter
        if stripped:
            current_chapter = stripped

    # Handle last annotation if file doesn't end with separator
    if in_annotation and text_lines:
        annotations.append(Annotation(
            book=book,
            chapter=current_chapter,
            page="",
            location=current_location,
            text=" ".join(text_lines),
            title=_title_from_text(" ".join(text_lines)),
            color=None,
        ))

    for i, a in enumerate(annotations, start=1):
        a.number = i

    # Attach figure references when EPUB figures are available
    if figure_map:
        for a in annotations:
            for label in detect_figure_refs(a.text):
                if label in figure_map:
                    a.figures.append(FigureRef(label=label))

    return annotations, figure_map
