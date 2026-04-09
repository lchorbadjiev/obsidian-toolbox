"""PDF figure extraction for Zotero annotations."""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

from otb.epub_figures import FigureMap


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
        result = extract_page_image(pdf_path, page_num)
        if result:
            figure_map[label] = result
        else:
            print(
                f"Warning: No image found on page {page_str} "
                f"for Figure {label}",
                file=sys.stderr,
            )
    return figure_map
