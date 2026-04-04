"""Tests for the highlight markdown parser."""
# pylint: disable=missing-function-docstring
from pathlib import Path

import pytest

from otb.parser import Book, Highlight
from otb.md_parser import parse_highlight_md, parse_highlight_dir

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "highlights"


@pytest.fixture
def highlights() -> list[Highlight]:
    return parse_highlight_dir(FIXTURES_DIR)


def test_count(highlights: list[Highlight]) -> None:
    assert len(highlights) == 4


def test_book_metadata(highlights: list[Highlight]) -> None:
    for h in highlights:
        assert h.book == Book(title="A Brief History of Time", author="Stephen Hawking")


def test_chapter_assignment(highlights: list[Highlight]) -> None:
    assert highlights[0].chapter == "1   Our Picture of the Universe"
    assert highlights[2].chapter == "2   Space and Time"


def test_page_and_location(highlights: list[Highlight]) -> None:
    assert highlights[0].page == 1
    assert highlights[0].location == 42
    assert highlights[2].page == 22
    assert highlights[2].location == 310


def test_no_color(highlights: list[Highlight]) -> None:
    for h in highlights:
        assert h.color is None


def test_text(highlights: list[Highlight]) -> None:
    assert highlights[0].text == "A well-known scientist once gave a public lecture on astronomy."
    assert "provisional" in highlights[1].text


def test_title(highlights: list[Highlight]) -> None:
    assert highlights[0].title == "A Well-Known Scientist Once Gave a Public Lecture on Astronomy"


def test_numbers(highlights: list[Highlight]) -> None:
    assert [h.number for h in highlights] == [1, 2, 3, 4]


def test_single_file() -> None:
    path = FIXTURES_DIR / "001 - A Well-Known Scientist Once Gave a Public Lecture on Astronomy.md"
    h = parse_highlight_md(path)
    assert h.page == 1
    assert h.location == 42
    assert h.book.author == "Stephen Hawking"
