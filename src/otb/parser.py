"""Parser for Kindle notebook HTML exports."""
import re
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup, Tag


@dataclass
class Book:
    """Metadata for a book."""

    title: str
    author: str


@dataclass
class Highlight:
    """A single Kindle highlight."""

    book: Book
    chapter: str
    color: str
    page: int
    location: int
    text: str


_NOTE_HEADING_RE = re.compile(
    r"Highlight\(\s*(\w+)\s*\)\s*-\s*Page\s+(\d+)\s*·\s*Location\s+(\d+)",
    re.IGNORECASE,
)


def _require(tag: Tag | None, desc: str) -> Tag:
    """Return tag or raise if missing."""
    if tag is None:
        raise ValueError(f"Required element not found: {desc}")
    return tag


def parse_notebook(path: Path) -> list[Highlight]:
    """Parse a Kindle notebook HTML export and return all highlights."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    title = _require(soup.find("div", class_="bookTitle"), "bookTitle").get_text(strip=True)
    authors_raw = _require(soup.find("div", class_="authors"), "authors").get_text(strip=True)
    # "Last, First" → "First Last"
    parts = [p.strip() for p in authors_raw.split(",", 1)]
    author = f"{parts[1]} {parts[0]}" if len(parts) == 2 else authors_raw
    book = Book(title=title, author=author)

    highlights: list[Highlight] = []
    current_chapter = ""
    pending: dict[str, str | int] | None = None

    body = _require(soup.find("div", class_="bodyContainer"), "bodyContainer")
    for div in body.find_all("div", recursive=False):
        if not isinstance(div, Tag):
            continue
        classes: list[str] = div.get("class") or []  # type: ignore[assignment]

        if "sectionHeading" in classes:
            current_chapter = div.get_text(strip=True)
            continue

        if "noteHeading" in classes:
            heading_text = div.get_text(strip=True)
            match = _NOTE_HEADING_RE.search(heading_text)
            if match:
                pending = {
                    "color": match.group(1),
                    "page": int(match.group(2)),
                    "location": int(match.group(3)),
                }
            else:
                pending = None
            continue

        if "noteText" in classes and pending is not None:
            highlights.append(
                Highlight(
                    book=book,
                    chapter=current_chapter,
                    color=str(pending["color"]),
                    page=int(pending["page"]),
                    location=int(pending["location"]),
                    text=div.get_text(strip=True),
                )
            )
            pending = None

    return highlights
