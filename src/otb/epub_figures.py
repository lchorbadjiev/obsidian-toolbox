"""EPUB figure extraction for Boox annotations."""
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

from bs4 import BeautifulSoup


# Maps figure label (e.g. "2.1") to (image_bytes, extension)
FigureMap = dict[str, tuple[bytes, str]]

_CAPTION_RE = re.compile(
    r"FIGURE\s+(\d+\.\d+[a-z]?)", re.IGNORECASE,
)


def detect_figure_refs(text: str) -> list[str]:
    """Detect figure references in annotation text.

    Returns a deduplicated list of figure labels in order of
    appearance (e.g. ["2.1", "2.3"]).
    """
    seen: set[str] = set()
    labels: list[str] = []
    for match in _CAPTION_RE.finditer(text):
        label = match.group(1)
        if label not in seen:
            seen.add(label)
            labels.append(label)
    return labels


def parse_epub_figures(epub_path: Path) -> FigureMap:
    """Parse an EPUB file and return a mapping of figure labels to images.

    Returns an empty dict if the EPUB is missing, corrupt, or contains
    no parseable figures. Warnings are printed to stderr.
    """
    if not epub_path.exists():
        print(
            f"Warning: EPUB not found: {epub_path}",
            file=sys.stderr,
        )
        return {}

    try:
        with zipfile.ZipFile(epub_path, "r") as zf:
            return _extract_figures(zf)
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        print(
            f"Warning: EPUB unreadable: {epub_path}: {exc}",
            file=sys.stderr,
        )
        return {}


def _extract_figures(  # pylint: disable=too-many-locals  # EPUB parsing tracks ZIP paths, HTML elements, and image data
    zf: zipfile.ZipFile,
) -> FigureMap:
    """Extract figure label → image data from an open EPUB ZIP."""
    xhtml_files = [
        n for n in zf.namelist()
        if n.endswith((".xhtml", ".html", ".htm"))
        and "META-INF" not in n
    ]

    figure_map: FigureMap = {}

    for xhtml_name in xhtml_files:
        html = zf.read(xhtml_name).decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        xhtml_dir = str(PurePosixPath(xhtml_name).parent)

        for fig in soup.find_all("figure"):
            img = fig.find("img")
            if not img:
                continue
            src = str(img.get("src", ""))
            if not src:
                continue

            # Extract figure label from figcaption text
            figcaption = fig.find("figcaption")
            if not figcaption:
                continue
            caption_text = figcaption.get_text()
            match = _CAPTION_RE.search(caption_text)
            if not match:
                continue

            label = match.group(1)

            # Resolve relative image path within the ZIP
            img_path = str(
                PurePosixPath(xhtml_dir) / PurePosixPath(src)
            )
            # Normalize (remove ../ segments)
            parts: list[str] = []
            for part in PurePosixPath(img_path).parts:
                if part == "..":
                    if parts:
                        parts.pop()
                else:
                    parts.append(part)
            resolved = str(PurePosixPath(*parts)) if parts else ""

            try:
                img_bytes = zf.read(resolved)
                ext = PurePosixPath(src).suffix or ".jpg"
                figure_map[label] = (img_bytes, ext)
            except KeyError:
                print(
                    f"Warning: Image not found in EPUB: {resolved}",
                    file=sys.stderr,
                )

    return figure_map
