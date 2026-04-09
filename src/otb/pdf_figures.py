"""PDF figure extraction for Zotero annotations."""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

from otb.epub_figures import FigureMap
from otb.parser import Annotation, _title_from_text


_FIGURE_RE = re.compile(
    r"(?:^|\b)[Ff]igure\s+(\d+[-.]?\d+[a-z]?)", re.IGNORECASE,
)
_GET_FIGURE_RE = re.compile(
    r"[Gg]et the figure\s+(\d+[-.]?\d+[a-z]?)",
)


def detect_zotero_figure_refs(
    text: str, page: str,
) -> list[tuple[str, str]]:
    """Detect figure references in Zotero annotation text.

    Returns a deduplicated list of (label, page_str) tuples.
    The page_str comes from the annotation metadata.
    """
    seen: set[str] = set()
    refs: list[tuple[str, str]] = []
    for pattern in (_FIGURE_RE, _GET_FIGURE_RE):
        for match in pattern.finditer(text):
            label = match.group(1)
            if label not in seen:
                seen.add(label)
                refs.append((label, page))
    return refs


def extract_page_image(
    pdf_path: Path, page_num: int,
) -> tuple[bytes, str] | None:
    """Extract the largest image from a PDF page.

    Returns (image_bytes, extension) or None if no images found.
    """
    try:
        reader = PdfReader(pdf_path)
        if page_num < 0 or page_num >= len(reader.pages):
            print(
                f"Warning: Page {page_num} out of range in {pdf_path}",
                file=sys.stderr,
            )
            return None
        page = reader.pages[page_num]
        images = page.images
        if not images:
            return None
        # Pick the largest image by data size
        best = max(images, key=lambda img: len(img.data))
        ext = Path(best.name).suffix or ".jpg"
        return (best.data, ext)
    except Exception as exc:  # pylint: disable=broad-exception-caught  # graceful fallback for corrupt PDFs
        print(
            f"Warning: PDF unreadable: {pdf_path}: {exc}",
            file=sys.stderr,
        )
        return None


def extract_pdf_figures(
    pdf_path: Path,
    refs: list[tuple[str, str]],
) -> FigureMap:
    """Extract figure images from PDF for all references.

    Each ref is (label, page_str). Returns a FigureMap mapping
    labels to (image_bytes, extension).
    """
    figure_map: FigureMap = {}
    for label, page_str in refs:
        try:
            page_num = int(page_str) - 1  # PDF is 0-indexed
        except (ValueError, TypeError):
            print(
                f"Warning: Invalid page '{page_str}' for "
                f"Figure {label}",
                file=sys.stderr,
            )
            continue
        result = _search_nearby_pages(pdf_path, page_num)
        if result:
            figure_map[label] = result
        else:
            print(
                f"Warning: No image found near page {page_str} "
                f"for Figure {label}",
                file=sys.stderr,
            )
    return figure_map


_SEARCH_RANGE = 5


def _search_nearby_pages(
    pdf_path: Path, center_page: int,
) -> tuple[bytes, str] | None:
    """Search for a figure image on the center page and nearby.

    Checks the center page first, then expands outward up to
    +/- _SEARCH_RANGE pages.
    """
    result = extract_page_image(pdf_path, center_page)
    if result:
        return result
    for offset in range(1, _SEARCH_RANGE + 1):
        for candidate in (center_page + offset, center_page - offset):
            result = extract_page_image(pdf_path, candidate)
            if result:
                return result
    return None


_MERGE_GAP_THRESHOLD = 10
_MATCH_CHARS = 30


def extract_page_text(pdf_path: Path, page_num: int) -> str:
    """Extract text content from a PDF page.

    Returns empty string on failure.
    """
    try:
        reader = PdfReader(pdf_path)
        if page_num < 0 or page_num >= len(reader.pages):
            return ""
        return reader.pages[page_num].extract_text() or ""
    except Exception:  # pylint: disable=broad-exception-caught  # graceful fallback
        return ""


def _are_adjacent_in_pdf(  # pylint: disable=too-many-locals  # text matching requires tracking multiple positions
    pdf_path: Path, text_a: str, page_a: int,
    text_b: str, page_b: int,
) -> bool:
    """Check if two annotation texts are adjacent in the PDF."""
    pdf_text_a = extract_page_text(pdf_path, page_a)
    pdf_text_b = extract_page_text(pdf_path, page_b)
    if not pdf_text_a or not pdf_text_b:
        return False

    # Normalize whitespace for matching (PDF text has newlines
    # where the original text has spaces or nothing)
    combined = " ".join((pdf_text_a + " " + pdf_text_b).split())

    # Use last/first few words for matching, stripping leading
    # punctuation to handle PDF spacing quirks (e.g., em-dash)
    words_a = text_a.split()
    words_b = text_b.split()
    tail = " ".join(words_a[-4:]) if len(words_a) > 4 else " ".join(words_a)
    # Strip leading non-alnum from first word of head for matching
    head_words = list(words_b[:4]) if len(words_b) > 4 else list(words_b)
    if head_words:
        head_words[0] = head_words[0].lstrip(
            "\u2014\u2013\u2012\u2010-\u201c\u201d\"'([{"
        )
    head = " ".join(head_words)

    if not tail or not head:
        return False

    pos_a = combined.find(tail)
    pos_b = combined.find(head, max(0, pos_a) if pos_a >= 0 else 0)

    if pos_a < 0 or pos_b < 0:
        return False

    gap = pos_b - (pos_a + len(tail))
    return 0 <= gap <= _MERGE_GAP_THRESHOLD


def merge_split_annotations(
    annotations: list[Annotation],
    pdf_path: Path | None,
) -> list[Annotation]:
    """Merge consecutive annotations split across page boundaries.

    When a PDF is available, checks if consecutive annotations on
    adjacent pages are adjacent in the PDF text (gap <= 10 chars).
    If so, merges them by concatenating text. Supports chained
    merges across 3+ pages.

    Returns the (possibly shorter) list of annotations.
    """
    if not pdf_path or len(annotations) < 2:
        return annotations

    merged: list[Annotation] = []
    i = 0
    while i < len(annotations):
        current = annotations[i]
        # Try to merge with subsequent annotations
        while i + 1 < len(annotations):
            nxt = annotations[i + 1]
            try:
                page_cur = int(current.page)
                page_nxt = int(nxt.page)
            except (ValueError, TypeError):
                break
            if page_nxt != page_cur + 1:
                break
            if current.color != nxt.color:
                break
            if not _are_adjacent_in_pdf(
                pdf_path, current.text, page_cur - 1,
                nxt.text, page_nxt - 1,
            ):
                break
            # Merge: concatenate text, keep first annotation's metadata
            current = Annotation(
                book=current.book,
                chapter=current.chapter,
                page=current.page,
                location=current.location,
                text=current.text + " " + nxt.text,
                title=_title_from_text(
                    current.text + " " + nxt.text
                ),
                color=current.color,
            )
            i += 1
        merged.append(current)
        i += 1

    return merged
