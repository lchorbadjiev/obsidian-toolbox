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
class Annotation:
    """A single Kindle annotation."""

    book: Book
    chapter: str
    page: str
    location: int
    text: str
    title: str = ""
    color: str | None = None
    number: int = 0
    anki_id: int | None = None


_SENTENCE_END_RE = re.compile(r"[.!?]")
_TITLE_MAX_WORDS = 7


def _title_from_text(text: str) -> str:
    """Return a title from the first sentence of text, capped at _TITLE_MAX_WORDS words."""
    m = _SENTENCE_END_RE.search(text)
    sentence = text[: m.start()] if m else text
    words = sentence.split()[:_TITLE_MAX_WORDS]
    return " ".join(words).title()


_NOTE_HEADING_RE = re.compile(
    r"Highlight\(\s*(\w+)\s*\)\s*-\s*(.+?)\s*·\s*Location\s+(\d+)",
    re.IGNORECASE,
)

def _parse_page_ref(raw: str) -> tuple[str, str]:
    """Parse a page reference from a noteHeading.

    Handles: 'Page 42', 'Page XVII',
    'Chapter 5: Title > Page 42', 'Chapter 1: Title'.
    Returns (page_string, chapter_from_heading).
    """
    chapter = ""
    page_str = ""

    if ">" in raw:
        # "Chapter 5: Title > Page 42"
        parts = raw.split(">", 1)
        chapter = parts[0].strip()
        page_part = parts[1].strip()
    elif raw.strip().lower().startswith("chapter"):
        # "Chapter 1: Title" with no page
        chapter = raw.strip()
        page_part = ""
    else:
        page_part = raw.strip()

    # Extract the page value from page_part like "Page 42"
    page_match = re.search(r"Page\s+(\S+)", page_part, re.IGNORECASE)
    if page_match:
        page_str = page_match.group(1)

    return page_str, chapter


def _parse_annotation(
    book: Book, chapter: str, pending: dict[str, str | int], text_div: Tag,
    generate_title: bool = True,
) -> Annotation:
    """Build an Annotation from a parsed noteHeading and its noteText div."""
    text = text_div.get_text(strip=True)
    return Annotation(
        book=book,
        chapter=chapter,
        page=str(pending["page"]),
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
) -> list[Annotation]:
    """Parse a Kindle notebook HTML export and return all annotations."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    title = _require(soup.find("div", class_="bookTitle"), "bookTitle").get_text(strip=True)
    authors_raw = _require(soup.find("div", class_="authors"), "authors").get_text(strip=True)
    # "Last, First" → "First Last"
    parts = [p.strip() for p in authors_raw.split(",", 1)]
    author = f"{parts[1]} {parts[0]}" if len(parts) == 2 else authors_raw
    book = Book(title=title, author=author)

    annotations: list[Annotation] = []
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
                page, heading_chapter = _parse_page_ref(match.group(2))
                if heading_chapter:
                    current_chapter = heading_chapter
                pending = {
                    "color": match.group(1),
                    "page": page,
                    "location": int(match.group(3)),
                }
            else:
                pending = None
            continue

        if "noteText" in classes and pending is not None:
            annotations.append(
                _parse_annotation(book, current_chapter, pending, div, generate_title)
            )
            pending = None

    for i, a in enumerate(annotations, start=1):
        a.number = i

    return annotations
