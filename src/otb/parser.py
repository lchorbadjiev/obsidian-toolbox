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
# pylint: disable=too-many-instance-attributes  # fixed data contract; fields cannot be reduced
class Highlight:
    """A single Kindle highlight."""

    book: Book
    chapter: str
    page: int
    location: int
    text: str
    title: str = ""
    color: str | None = None
    number: int = 0


_SENTENCE_END_RE = re.compile(r"[.!?]")
_TITLE_MAX_WORDS = 7


def _title_from_text(text: str) -> str:
    """Return a title from the first sentence of text, capped at _TITLE_MAX_WORDS words."""
    m = _SENTENCE_END_RE.search(text)
    sentence = text[: m.start()] if m else text
    words = sentence.split()[:_TITLE_MAX_WORDS]
    return " ".join(words).title()


_NOTE_HEADING_RE = re.compile(
    r"Highlight\(\s*(\w+)\s*\)\s*-\s*Page\s+(\d+)\s*·\s*Location\s+(\d+)",
    re.IGNORECASE,
)


def _parse_highlight(
    book: Book, chapter: str, pending: dict[str, str | int], text_div: Tag,
    generate_title: bool = True,
) -> Highlight:
    """Build a Highlight from a parsed noteHeading and its noteText div."""
    text = text_div.get_text(strip=True)
    return Highlight(
        book=book,
        chapter=chapter,
        page=int(pending["page"]),
        location=int(pending["location"]),
        text=text,
        title=_title_from_text(text) if generate_title else "",
        color=str(pending["color"]),
    )


def _require(tag: Tag | None, desc: str) -> Tag:
    """Return tag or raise if missing."""
    if tag is None:
        raise ValueError(f"Required element not found: {desc}")
    return tag


def parse_notebook(  # pylint: disable=too-many-locals  # sequential HTML parsing requires tracking several state variables
    path: Path, generate_title: bool = True
) -> list[Highlight]:
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
            highlights.append(_parse_highlight(book, current_chapter, pending, div, generate_title))
            pending = None

    for i, h in enumerate(highlights, start=1):
        h.number = i

    return highlights
