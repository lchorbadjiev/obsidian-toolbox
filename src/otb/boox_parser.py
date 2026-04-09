"""Parser for Boox e-reader annotation exports."""
import re
from pathlib import Path

from otb.parser import Annotation, _title_from_text
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


def parse_boox_annotations(
    directory: Path,
) -> list[Annotation]:
    """Parse Boox annotation exports from a directory.

    The directory must contain book.txt and exactly one other .txt
    annotation file. Returns a list of Annotation objects with
    sequential numbering.

    Raises FileNotFoundError if book.txt or the annotation file
    is missing.
    """
    book = parse_book_metadata(directory / "book.txt")
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

    return annotations
